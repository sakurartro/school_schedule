from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import CustomEmoji, Text
from aiogram.enums import ParseMode
from yandex_download import YandexDiskParsing

from config import SCHOOL_EMOJI
from tg.keyboard import main_keyboard, disclaimer_kb, grades_kb, grades2_kb
from table_to_python import FileWork
from service import get_data_id, add_user_link, change_grade

router = Router()


class Registration(StatesGroup):
    waiting_for_link = State()


async def send_welcome(message: Message) -> None:
    emoji_id, fallback = SCHOOL_EMOJI["school_building_small"]
    content = Text(
        CustomEmoji(fallback, custom_emoji_id=emoji_id),
        f" Привет, {message.from_user.first_name}!\n\n"
        "Я показываю расписание уроков.\n"
        "/today — расписание на сегодня\n"
        "/week — расписание на всю неделю\n\n"
        "Загляни в меню снизу 👇",
    )
    await message.answer(**content.as_kwargs(), reply_markup=main_keyboard)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = await get_data_id(message.from_user.id)
    if user and user.table_link:
        await send_welcome(message)
        return None

    await message.answer(
        "⚠️ Перед началом работы:\n\n"
        "Расписание берётся из таблицы, которую пришлёшь ты сам. "
        "Я не проверяю её актуальность и корректность — если расписание окажется "
        "неверным или устаревшим, ответственность за это несёшь ты, а не бот.\n\n"
        "Нажимая кнопку ниже, ты подтверждаешь, что понимаешь это.",
        reply_markup=await disclaimer_kb(),
    )


@router.callback_query(F.data == "accept_disclaimer")
async def accept_disclaimer(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.answer(
        "Пришли ссылку на публичную таблицу с расписанием на Яндекс.Диске, "
        "чтобы я мог показывать твоё расписание."
    )
    await state.set_state(Registration.waiting_for_link)


@router.message(Registration.waiting_for_link)
async def grade_ask(message: Message, state: FSMContext) -> None:
    table_link = (message.text or "").strip()
    if not table_link.startswith("http"):
        await message.answer("Это не похоже на ссылку. Пришли ссылку на таблицу на Яндекс.Диске")
        return None
    file_path = f"tables/{message.from_user.id}.xlsx"
    yandex = YandexDiskParsing(table_link, file_path=file_path)

    await yandex.download_data()

    calamaine = FileWork(file_path, message.from_user.id)

    grades = calamaine.get_all_sheets()

    await message.answer("Выбери класс", reply_markup=await grades_kb(grades))
    await state.update_data(link=table_link, path=file_path)
    


@router.callback_query(F.data.startswith("grade_"))
async def set_data(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    link = data.get("link", "")
    path = data.get("path", "")
    callback_text = callback.data
    grade = callback_text.strip().split("grade_")[-1]
    await add_user_link(chatid=callback.message.chat.id, tg_id=callback.from_user.id, table_link=link, grade=grade, file_path=path)
    
    emoji_id, fallback = SCHOOL_EMOJI["school_building_small"]
    content = Text(
        CustomEmoji(fallback, custom_emoji_id=emoji_id),
        f" Привет, {callback.from_user.first_name}!\n\n"
        "Я показываю расписание уроков.\n"
        "/today — расписание на сегодня\n"
        "/week — расписание на всю неделю\n\n"
        "Загляни в меню снизу 👇",
    )
    await callback.message.answer(**content.as_kwargs(), reply_markup=main_keyboard)
    await state.clear()


@router.callback_query(F.data == "support")
async def donation_page(callback: CallbackQuery) -> None:
    await callback.answer()
    text = f"""
    <tg-emoji emoji-id=\"5350781673103453057\">🔐</tg-emoji>Поддержка\n
    <tg-emoji emoji-id=\"5350427449970679463\">✈️</tg-emoji> Telegram: @ayeshaio1337
    <tg-emoji emoji-id=\"5346181118884331907\">📱</tg-emoji> Github: <code>github.com/sakurartro/school_schedule</code>
    ---------------------------------------------------------
    <tg-emoji emoji-id=\"5350641884802870510\">💲</tg-emoji>Донат\n
    <tg-emoji emoji-id=\"5350641884802870510\">💲</tg-emoji> Рубли: <code>2202208527289756</code>
    <tg-emoji emoji-id=\"5296742257146241213\">💎</tg-emoji> GRAM:  <code>UQDaKwq6d0atM7efEfuTuvdAJdc-C6r5ZSn0N8MY6LPQ2dIY</code>\n
    """
    await callback.message.answer(text, parse_mode=ParseMode.HTML)


@router.message(Command("change_grade"))
async def change_grade_command(message: Message):
    tg_id = message.from_user.id
    data = await get_data_id(tg_id)
    if data is None:
        await message.answer("Ошибка базы данных")
        return
    
    calamine = FileWork(data.file_path, tg_id)

    grades = calamine.get_all_sheets()

    await message.answer("Выберите новый класс: ", reply_markup=await grades2_kb(grades))



@router.callback_query(F.data.startswith("grade2_"))
async def update_grade(callback: CallbackQuery):
    await callback.answer()
    data = callback.data
    new_grade = data.strip().split("grade2_")[-1]
    await change_grade(callback.from_user.id, new_grade)
    await callback.message.answer(f"Класс успешно сменён на: {new_grade}")
