from html import escape

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, LinkPreviewOptions, Message

import tg.keyboard as kb
from service import delete_profile, get_data_id
from tg.keyboard import BTN_PROFILE
from tg.texts import NO_PROFILE, grade_label

router = Router()


class Redirict(StatesGroup):
    redirict = State()


@router.message(Command("profile"))
@router.message(F.text == BTN_PROFILE)
async def show_profile(message: Message) -> None:
    data = await get_data_id(message.from_user.id)
    if data is None or not data.table_link:
        await message.answer(NO_PROFILE)
        return None

    text = (
        f'<tg-emoji emoji-id="5350781673103453057">🔐</tg-emoji> Профиль — '
        f"{escape(message.from_user.first_name)}\n"
        f'<tg-emoji emoji-id="5350809912513424561">🔊</tg-emoji> Класс — '
        f"{escape(grade_label(data.grade, data.class_letter) if data.grade else '—')}\n"
        f'<tg-emoji emoji-id="5271604874419647061">🔗</tg-emoji> Расписание — '
        f"<a href=\"{escape(data.table_link, quote=True)}\">таблица</a>\n\n"
        f'<tg-emoji emoji-id="5420323339723881652">⚠️</tg-emoji> '
        f"Удалить аккаунт — /delete"
    )
    await message.answer(
        text,
        parse_mode=ParseMode.HTML,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        reply_markup=await kb.profile_kb(),
    )


@router.message(Command("delete"))
@router.callback_query(F.data == "delete_profile")
async def delete_profile_msg(event: Message | CallbackQuery) -> None:
    if isinstance(event, CallbackQuery):
        await event.answer()
        message = event.message
    else:
        message = event

    await message.answer(
        '<tg-emoji emoji-id="5420323339723881652">⚠️</tg-emoji> '
        "Вы точно хотите удалить свой профиль?",
        parse_mode=ParseMode.HTML,
        reply_markup=await kb.delete_kb(),
    )


@router.callback_query(F.data == "yes")
async def delete_profile_func(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await delete_profile(callback.from_user.id)
    await callback.message.edit_text("Профиль успешно удалён!")
    await state.set_state(Redirict.redirict)


@router.message()
async def unknown_message(message: Message) -> None:
    """Ловим всё, что не разобрали остальные роутеры, — иначе бот молчит в ответ."""
    await message.answer(
        "🤔 Не понял. Посмотри, что я умею — /help",
        reply_markup=kb.main_keyboard,
    )
