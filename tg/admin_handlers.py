from html import escape

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from service import get_all_data
from tg.texts import grade_label

router = Router()

ADMIN_USERNAME = "colalaflare1337"

# запас от лимита Telegram в 4096 символов на сообщение
MAX_CHUNK_LEN = 3500


def _is_admin(message: Message) -> bool:
    username = (message.from_user.username or "").lower()
    return username == ADMIN_USERNAME.lower()


def _format_user(index: int, user) -> str:
    link = f'<a href="tg://user?id={user.tg_id}">{user.tg_id}</a>'
    if not user.grade or not user.table_link:
        return f"{index}. {link} — ⚠️ регистрация не завершена"
    return f"{index}. {link} — {escape(grade_label(user.grade, user.class_letter))}"


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not _is_admin(message):
        await message.answer("⛔ Эта команда только для администратора")
        return None

    users = await get_all_data()
    if not users:
        await message.answer("📭 В базе пока нет пользователей")
        return None

    lines = [_format_user(i, user) for i, user in enumerate(users, start=1)]

    chunk = f"👥 <b>Пользователи бота</b> — всего: {len(users)}\n\n"
    for line in lines:
        if len(chunk) + len(line) + 1 > MAX_CHUNK_LEN:
            await message.answer(chunk, parse_mode=ParseMode.HTML)
            chunk = ""
        chunk += line + "\n"
    if chunk.strip():
        await message.answer(chunk, parse_mode=ParseMode.HTML)
