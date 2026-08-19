from datetime import datetime, timedelta, timezone

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

BTN_TODAY = "Сегодня"
BTN_TOMMOROW = "Завтра"
BTN_WEEK = "Неделя"
BTN_PROFILE = "Профиль"
BTN_HELP = "Помощь"

SCHOOL_TZ = timezone(timedelta(hours=7))

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=BTN_TODAY, icon_custom_emoji_id="5224607267797606837"),
            KeyboardButton(text=BTN_TOMMOROW, icon_custom_emoji_id="5456140674028019486"),
        ],
        [
            KeyboardButton(text=BTN_WEEK, icon_custom_emoji_id="5413879192267805083"),
            KeyboardButton(text=BTN_PROFILE, icon_custom_emoji_id="5350781673103453057"),
        ],
        [KeyboardButton(text=BTN_HELP, icon_custom_emoji_id="5436113877181941026")],
    ],
    resize_keyboard=True,
    is_persistent=True,
    input_field_placeholder="Выбери, что показать 👇",
)


async def grades_kb(grades: list[str], prefix: str = "grade") -> InlineKeyboardMarkup:
    """Классы отдаём индексом: название листа может не влезть в 64 байта callback_data."""
    builder = InlineKeyboardBuilder()

    for idx, grade in enumerate(grades):
        builder.add(InlineKeyboardButton(text=grade, callback_data=f"{prefix}_{idx}"))

    return builder.adjust(2).as_markup()


async def letters_kb(letters: list[str], prefix: str = "letter") -> InlineKeyboardMarkup:
    """Буква класса умещается в callback_data целиком — индекс тут не нужен."""
    builder = InlineKeyboardBuilder()

    for letter in letters:
        builder.add(InlineKeyboardButton(text=letter, callback_data=f"{prefix}_{letter}"))

    return builder.adjust(4).as_markup()


async def disclaimer_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Понимаю и принимаю", callback_data="accept_disclaimer"))
    return builder.adjust(1).as_markup()


async def info_kb(is_sh: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_sh:
        time_now = datetime.now(tz=SCHOOL_TZ).strftime("%H:%M")
        builder.add(InlineKeyboardButton(text=f"Обновлено: {time_now}", callback_data="time"))
    builder.add(InlineKeyboardButton(text="Поддержка", callback_data="support"))
    return builder.adjust(1).as_markup()


async def profile_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Сменить класс", callback_data="change_grade"))
    builder.add(InlineKeyboardButton(text="Сменить таблицу", callback_data="change_schedule"))
    builder.add(InlineKeyboardButton(text="Удалить профиль", callback_data="delete_profile"))
    builder.add(InlineKeyboardButton(text="Поддержка", callback_data="support"))
    return builder.adjust(2, 2).as_markup()


async def delete_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Да, удалить", callback_data="yes"))
    builder.add(InlineKeyboardButton(text="Отмена", callback_data="no"))
    return builder.adjust(2).as_markup()
