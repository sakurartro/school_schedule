from aiogram.types import Message
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.utils.formatting import CustomEmoji, Text

from config import SCHOOL_EMOJI
from tg.keyboard import main_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    emoji_id, fallback = SCHOOL_EMOJI["school_building_small"]
    content = Text(
        CustomEmoji(fallback, custom_emoji_id=emoji_id),
        f" Привет, {message.from_user.first_name}!\n\n"
        "Я показываю расписание уроков.\n"
        "📅 Сегодня — расписание на сегодня\n"
        "🗓 Неделя — расписание на всю неделю\n\n"
        "Загляни в меню снизу 👇",
    )
    await message.answer(**content.as_kwargs(), reply_markup=main_keyboard)
