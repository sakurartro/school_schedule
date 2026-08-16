from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.formatting import CustomEmoji, Text

from config import SCHOOL_EMOJI
from tg.keyboard import BTN_HELP, main_keyboard

router = Router()


@router.message(Command("help"))
@router.message(F.text == BTN_HELP)
async def cmd_help(message: Message) -> None:
    emoji_id, fallback = SCHOOL_EMOJI["owl_grad_cap"]
    content = Text(
        CustomEmoji(fallback, custom_emoji_id=emoji_id),
        " Что я умею:\n\n"
        "/day — расписание на сегодня\n"
        "/week — расписание на всю неделю",
    )
    await message.answer(**content.as_kwargs(), reply_markup=main_keyboard)
