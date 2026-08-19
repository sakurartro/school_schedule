from datetime import datetime

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import InputRichMessage, Message

import tg.keyboard as kb
from client import get_latest_schedule_week
from data_content import find_day
from service import get_data_id, save_schedule
from tg.keyboard import BTN_TODAY, BTN_TOMMOROW, BTN_WEEK, SCHOOL_TZ
from tg.rich_render import emoji_heading, schedule_table_week
from tg.texts import LOAD_ERROR, NO_PROFILE

router = Router()


async def load_week(message: Message):
    """Проверяем профиль и тянем свежее расписание. None — пользователю уже ответили."""
    user = await get_data_id(message.from_user.id)
    if user is None or not user.table_link or not user.grade:
        await message.answer(NO_PROFILE)
        return None

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    week_schedule = await get_latest_schedule_week(
        message.from_user.id, user.table_link, user.grade, user.class_letter
    )
    if not week_schedule:
        await message.answer(LOAD_ERROR)
        return None
    return week_schedule


@router.message(Command("week"))
@router.message(F.text == BTN_WEEK)
async def sent_schedule_week(message: Message) -> None:
    week_schedule = await load_week(message)
    if week_schedule is None:
        return None

    rich_msg = InputRichMessage(
        blocks=[
            emoji_heading("на неделю", "calendar_september_1"),
            schedule_table_week(week_schedule),
        ]
    )
    await message.answer_rich(rich_msg, reply_markup=await kb.info_kb(True))
    await save_schedule(
        chatid=message.chat.id, tg_id=message.from_user.id, schedule=week_schedule
    )


async def send_day(message: Message, offset: int) -> None:
    week_schedule = await load_week(message)
    if week_schedule is None:
        return None

    weekday = datetime.now(tz=SCHOOL_TZ).weekday() + offset
    schedule = find_day(week_schedule, weekday)
    if schedule is None:
        when = "сегодня" if offset == 0 else "завтра"
        await message.answer(f"📭 На {when} расписания нет")
        return None

    rich_msg = InputRichMessage(
        blocks=[
            emoji_heading(schedule.weekday, "alarm_clock"),
            schedule_table_week([schedule]),
        ]
    )
    await message.answer_rich(rich_message=rich_msg, reply_markup=await kb.info_kb(True))
    await save_schedule(
        chatid=message.chat.id, tg_id=message.from_user.id, schedule=week_schedule
    )


@router.message(Command("today"))
@router.message(F.text == BTN_TODAY)
async def sent_schedule_today(message: Message) -> None:
    await send_day(message, offset=0)


@router.message(Command("tomorrow"))
@router.message(F.text == BTN_TOMMOROW)
async def sent_schedule_tomorrow(message: Message) -> None:
    await send_day(message, offset=1)


@router.callback_query(F.data == "time")
async def show_update_time(callback) -> None:
    await callback.answer("Расписание обновляется при каждом запросе 👌", show_alert=False)
