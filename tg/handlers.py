import asyncio
import os

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from client import table_path
from service import add_user_link, change_grade, get_data_id
from table_to_python import FileWork
from tg.keyboard import disclaimer_kb, grades_kb, letters_kb, main_keyboard
from tg.texts import (
    ASK_LINK,
    BAD_LINK,
    CHOOSE_LETTER,
    DISCLAIMER,
    DOWNLOAD_ERROR,
    NO_PROFILE,
    NO_SHEETS,
    STALE_GRADES,
    grade_label,
    welcome_content,
)
from tg.user_handlers import Redirict
from yandex_download import YandexDiskParsing, is_yandex_link

router = Router()


class Registration(StatesGroup):
    waiting_for_link = State()


def pick_grade(grades: list[str], callback_data: str, prefix: str) -> str | None:
    index = callback_data.removeprefix(prefix)
    if not index.isdigit() or int(index) >= len(grades):
        return None
    return grades[int(index)]


async def send_welcome(message: Message, name: str) -> None:
    content = welcome_content(name)
    await message.answer(**content.as_kwargs(), reply_markup=main_keyboard)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    if await state.get_state() is None:
        await message.answer("Нечего отменять")
        return None
    await state.clear()
    await message.answer("Действие отменено", reply_markup=main_keyboard)


@router.callback_query(F.data == "no")
@router.message(CommandStart())
@router.message(Redirict.redirict)
async def cmd_start(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if isinstance(event, CallbackQuery):
        await event.answer()
        message = event.message
    else:
        message = event

    user = await get_data_id(event.from_user.id)
    if user and user.table_link:
        await send_welcome(message, event.from_user.first_name)
        return None

    await message.answer(DISCLAIMER, reply_markup=await disclaimer_kb())


@router.callback_query(F.data == "accept_disclaimer")
async def accept_disclaimer(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.answer(ASK_LINK)
    await state.set_state(Registration.waiting_for_link)


@router.message(Registration.waiting_for_link)
async def grade_ask(message: Message, state: FSMContext) -> None:
    table_link = (message.text or "").strip()
    if not is_yandex_link(table_link):
        await message.answer(BAD_LINK)
        return None

    status = await message.answer("⏳ Загружаю таблицу...")

    file_path = table_path(message.from_user.id)
    yandex = YandexDiskParsing(table_link, file_path=file_path)
    if not await yandex.download_data():
        await status.edit_text(DOWNLOAD_ERROR)
        return None

    grades = await asyncio.to_thread(FileWork(file_path).get_all_sheets)
    if not grades:
        await status.edit_text(NO_SHEETS)
        return None

    await state.update_data(link=table_link, path=file_path, grades=grades)
    await status.edit_text("Выбери свой класс:", reply_markup=await grades_kb(grades))


async def finish_registration(
    callback: CallbackQuery, state: FSMContext, link: str, file_path: str, grade: str, letter: str | None
) -> None:
    await add_user_link(
        chatid=callback.message.chat.id,
        tg_id=callback.from_user.id,
        table_link=link,
        grade=grade,
        class_letter=letter,
        file_path=file_path,
    )
    await state.clear()
    await callback.message.edit_text(f"✅ Класс выбран: {grade_label(grade, letter)}")
    await send_welcome(callback.message, callback.from_user.first_name)


@router.callback_query(F.data.startswith("grade_"))
async def set_data(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    grade = pick_grade(data.get("grades", []), callback.data or "", "grade_")
    if grade is None:
        await callback.message.answer(STALE_GRADES)
        await state.clear()
        return None

    file_path = data.get("path", "")
    letters = await asyncio.to_thread(FileWork(file_path).get_class_letters, grade)
    if len(letters) <= 1:
        await finish_registration(
            callback, state, data.get("link", ""), file_path, grade, letters[0] if letters else None
        )
        return None

    await state.update_data(grade=grade, letters=letters)
    await callback.message.edit_text(CHOOSE_LETTER, reply_markup=await letters_kb(letters))


@router.callback_query(F.data.startswith("letter_"))
async def set_letter(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    letter = (callback.data or "").removeprefix("letter_")
    grade = data.get("grade")
    if not grade or letter not in data.get("letters", []):
        await callback.message.answer(STALE_GRADES)
        await state.clear()
        return None

    await finish_registration(callback, state, data.get("link", ""), data.get("path", ""), grade, letter)


async def ask_new_grade(message: Message, tg_id: int, state: FSMContext) -> None:
    user = await get_data_id(tg_id)
    if user is None or not user.table_link:
        await message.answer(NO_PROFILE)
        return None

    file_path = user.file_path or table_path(tg_id)
    if not os.path.exists(file_path):
        await YandexDiskParsing(user.table_link, file_path=file_path).download_data()

    grades = await asyncio.to_thread(FileWork(file_path).get_all_sheets)
    if not grades:
        await message.answer("⚠️ Не удалось прочитать таблицу. Попробуй сменить её — /change_schedule")
        return None

    await state.update_data(grades=grades, path=file_path)
    await message.answer("Выбери новый класс:", reply_markup=await grades_kb(grades, prefix="grade2"))


@router.message(Command("change_grade"))
async def change_grade_command(message: Message, state: FSMContext) -> None:
    await ask_new_grade(message, message.from_user.id, state)


@router.callback_query(F.data == "change_grade")
async def change_grade_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await ask_new_grade(callback.message, callback.from_user.id, state)


async def finish_grade_change(callback: CallbackQuery, state: FSMContext, grade: str, letter: str | None) -> None:
    await change_grade(callback.from_user.id, grade, letter)
    await state.clear()
    await callback.message.edit_text(f"✅ Класс успешно сменён на: {grade_label(grade, letter)}")


@router.callback_query(F.data.startswith("grade2_"))
async def update_grade(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    grade = pick_grade(data.get("grades", []), callback.data or "", "grade2_")
    if grade is None:
        await callback.message.answer(STALE_GRADES)
        return None

    file_path = data.get("path", "")
    letters = await asyncio.to_thread(FileWork(file_path).get_class_letters, grade)
    if len(letters) <= 1:
        await finish_grade_change(callback, state, grade, letters[0] if letters else None)
        return None

    await state.update_data(grade=grade, letters=letters)
    await callback.message.edit_text(CHOOSE_LETTER, reply_markup=await letters_kb(letters, prefix="letter2"))


@router.callback_query(F.data.startswith("letter2_"))
async def update_letter(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    letter = (callback.data or "").removeprefix("letter2_")
    grade = data.get("grade")
    if not grade or letter not in data.get("letters", []):
        await callback.message.answer(STALE_GRADES)
        return None

    await finish_grade_change(callback, state, grade, letter)


@router.message(Command("change_schedule"))
async def change_table_url_cmd(message: Message, state: FSMContext) -> None:
    await message.answer(ASK_LINK)
    await state.set_state(Registration.waiting_for_link)


@router.callback_query(F.data == "change_schedule")
async def change_table_url_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.answer(ASK_LINK)
    await state.set_state(Registration.waiting_for_link)
