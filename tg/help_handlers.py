from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import CustomEmoji, Text
from aiogram.enums import ParseMode

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