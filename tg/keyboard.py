from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from datetime import datetime, timezone, timedelta
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder

BTN_TODAY = "Сегодня"
BTN_TOMMOROW = "Завтра"
BTN_WEEK = "Неделя"
BTN_HELP = "Помощь"

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_TODAY, icon_custom_emoji_id="5224607267797606837"), KeyboardButton(text=BTN_TOMMOROW, icon_custom_emoji_id="5456140674028019486")],
        [KeyboardButton(text=BTN_WEEK, icon_custom_emoji_id="5413879192267805083")],
        [KeyboardButton(text=BTN_HELP, icon_custom_emoji_id="5436113877181941026")],
    ],
    resize_keyboard=True,
    is_persistent=True,
)

async def grades_kb(grades: list):
    builder = InlineKeyboardBuilder()

    for grade in grades:
        builder.add(InlineKeyboardButton(text=grade, callback_data=f"grade_{grade}"))

    return builder.adjust(2).as_markup()


async def grades2_kb(grades: list):
    builder = InlineKeyboardBuilder()

    for grade in grades:
        builder.add(InlineKeyboardButton(text=grade, callback_data=f"grade2_{grade}"))

    return builder.adjust(2).as_markup()


async def disclaimer_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Понимаю и принимаю", callback_data="accept_disclaimer"))
    return builder.adjust(1).as_markup()


async def info_kb(is_sh: bool = False):
    builder = InlineKeyboardBuilder()
    utc_plus_seven = timezone(timedelta(hours=7))
    time_now = datetime.now(tz=utc_plus_seven)
    time_now = time_now.strftime("%H:%M")
    if is_sh:
        builder.add(InlineKeyboardButton(text=f"Обновлено: {time_now}", callback_data="time"))
    builder.add(InlineKeyboardButton(text="Поддержка", callback_data="support"))
    return builder.adjust(1).as_markup()


async def delete_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Да", callback_data="yes"))
    builder.add(InlineKeyboardButton(text="Нет", callback_data="no"))
    return builder.adjust(2).as_markup()