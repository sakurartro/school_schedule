from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from tg.keyboard import BTN_PREMIUM

router = Router()


@router.message(Command("premium"))
@router.message(F.text == BTN_PREMIUM)
async def cmd_premium(message: Message) -> None:
    await message.answer("⭐ Premium-подписка скоро появится.")
