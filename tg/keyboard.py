from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from datetime import datetime, timezone, timedelta
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder

BTN_TODAY = "📅 Сегодня"
BTN_TOMMOROW = "🗓️ Завтра"
BTN_WEEK = "🗓 Неделя"
BTN_HELP = "❓ Помощь"

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_TOMMOROW)],
        [KeyboardButton(text=BTN_TODAY), KeyboardButton(text=BTN_WEEK)],
        [KeyboardButton(text=BTN_HELP)],
    ],
    resize_keyboard=True,
    is_persistent=True,
)

async def grades_kb(grades: list):
    builder = InlineKeyboardBuilder()

    for grade in grades:
        builder.add(InlineKeyboardButton(text=grade, callback_data=f"grade_{grade}"))

    return builder.adjust(2).as_markup()


async def disclaimer_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Понимаю и принимаю", callback_data="accept_disclaimer"))
    return builder.adjust(1).as_markup()


async def info_kb():
    builder = InlineKeyboardBuilder()
    utc_plus_seven = timezone(timedelta(hours=7))
    time_now = datetime.now(tz=utc_plus_seven)
    time_now = time_now.strftime("%H:%M")
    builder.add(InlineKeyboardButton(text=f"Обновлено: {time_now}", callback_data="time"))
    builder.add(InlineKeyboardButton(text="Поддержка", callback_data="support"))
    return builder.adjust(1).as_markup()
