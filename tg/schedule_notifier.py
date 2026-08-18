from client import get_latest_schedule_week
from datetime import datetime
from service import get_all_data, add_data
from dataclasses import asdict
from aiogram import Bot
from data_content import find_day, find_day_dict
from aiogram.types import InputRichMessage
from tg.rich_render import schedule_table_week, emoji_heading
import tg.keyboard as kb
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from tg.tg_bot_init import bot


scheduler = AsyncIOScheduler()

async def scheduled_msg(bot: Bot) -> None:
    weekday = datetime.now().weekday()

    for data in await get_all_data():
        if not data.table_link:
            continue

        week_schedule = await get_latest_schedule_week(data.tg_id, data.table_link)
        if not isinstance(week_schedule, list):
            continue

        schedule = find_day(week_schedule, weekday)
        if schedule is None:
            continue

        today_dict = asdict(schedule)
        past_lessons = (
            find_day_dict(data.last_schedule, weekday)
            if data.last_schedule is not None
            else None
        )
        if past_lessons == today_dict:
            continue

        schedule2 = find_day(week_schedule, weekday + 1)

        rich_msg = InputRichMessage(
            blocks=[
                emoji_heading(schedule.weekday, "alarm_clock"),
                schedule_table_week([schedule, schedule2])
            ]
        )

        await bot.send_rich_message(chat_id=data.chat_id, rich_message=rich_msg, reply_markup=await kb.info_kb())
        await add_data(chatid=data.chat_id, tg_id=data.tg_id, schedule=week_schedule)


scheduler.add_job(scheduled_msg, IntervalTrigger(minutes=30), args=[bot])  