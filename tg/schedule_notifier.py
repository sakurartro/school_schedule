import logging
from dataclasses import asdict
from datetime import datetime

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import InputRichMessage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

import tg.keyboard as kb
from client import get_latest_schedule_week
from data_content import find_day, find_day_dict
from service import get_all_data, save_schedule
from tg.keyboard import SCHOOL_TZ
from tg.rich_render import emoji_heading, schedule_table_week
from tg.tg_bot_init import bot

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def notify_user(bot: Bot, data, weekday: int) -> None:
    week_schedule = await get_latest_schedule_week(
        data.tg_id, data.table_link, data.grade, data.class_letter
    )
    if not week_schedule:
        return None

    schedule = find_day(week_schedule, weekday)
    if schedule is None:
        return None

    past_lessons = (
        find_day_dict(data.last_schedule, weekday) if data.last_schedule else None
    )
    if past_lessons == asdict(schedule):
        return None

    days = [schedule]
    tomorrow = find_day(week_schedule, weekday + 1)
    if tomorrow is not None:
        days.append(tomorrow)

    rich_msg = InputRichMessage(
        blocks=[
            emoji_heading(schedule.weekday, "alarm_clock"),
            schedule_table_week(days),
        ]
    )

    await bot.send_rich_message(
        chat_id=data.chat_id, rich_message=rich_msg, reply_markup=await kb.info_kb()
    )
    await save_schedule(chatid=data.chat_id, tg_id=data.tg_id, schedule=week_schedule)


async def scheduled_msg(bot: Bot) -> None:
    weekday = datetime.now(tz=SCHOOL_TZ).weekday()

    for data in await get_all_data():
        if not data.table_link or not data.grade:
            continue
        try:
            await notify_user(bot, data, weekday)
        except TelegramAPIError as e:
            logger.warning("Не удалось отправить расписание %s: %s", data.tg_id, e)
        except Exception as e:
            logger.exception("Ошибка рассылки для %s: %s", data.tg_id, e)


scheduler.add_job(
    scheduled_msg,
    IntervalTrigger(minutes=30),
    args=[bot],
    max_instances=1,
    coalesce=True,
)
