from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from tg.keyboard import BTN_HELP, main_keyboard
from tg.texts import help_content

router = Router()

SUPPORT_TEXT = (
    '<tg-emoji emoji-id="5350781673103453057">🔐</tg-emoji> <b>Поддержка</b>\n\n'
    '<tg-emoji emoji-id="5350427449970679463">✈️</tg-emoji> Telegram: @colalaflare1337\n\n'
    '<tg-emoji emoji-id="5350641884802870510">💲</tg-emoji> <b>Донат</b>\n\n'
    '<tg-emoji emoji-id="5296742257146241213">💎</tg-emoji> GRAM: '
    "<code>UQDaKwq6d0atM7efEfuTuvdAJdc-C6r5ZSn0N8MY6LPQ2dIY</code>"
)


@router.message(Command("help"))
@router.message(F.text == BTN_HELP)
async def cmd_help(message: Message) -> None:
    content = help_content()
    await message.answer(**content.as_kwargs(), reply_markup=main_keyboard)


@router.callback_query(F.data == "support")
async def donation_page(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(SUPPORT_TEXT, parse_mode=ParseMode.HTML)
