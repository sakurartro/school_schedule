from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder

BTN_TODAY = "📅 Сегодня"
BTN_WEEK = "🗓 Неделя"
BTN_HELP = "❓ Помощь"
BTN_PREMIUM = "⭐ Premium"

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_TODAY), KeyboardButton(text=BTN_WEEK)],
        [KeyboardButton(text=BTN_HELP), KeyboardButton(text=BTN_PREMIUM)],
    ],
    resize_keyboard=True,
    is_persistent=True,
)

async def donate_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Поддержать разработчика", callback_data="donate"))
    return builder.adjust(1).as_markup()