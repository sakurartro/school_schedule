from aiogram.types import (
    Message,
    InputRichMessage,
    InputRichBlockSectionHeading,
    InputRichBlockTable,
    RichBlockTableCell,
    RichTextCustomEmoji,
)
from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from client import get_latest_schedule_week
from dataclasses import asdict
from tg.tg_bot_init import bot
from service import add_data, get_all_data, add_lessons
from data_content import find_day, find_day_dict
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import SCHOOL_EMOJI
from tg.keyboard import BTN_TODAY, BTN_WEEK

scheduler = AsyncIOScheduler()

router = Router()


def emoji_heading(weekday: str, emoji_key: str, size: int = 2) -> InputRichBlockSectionHeading:
    emoji_id, fallback = SCHOOL_EMOJI[emoji_key]
    return InputRichBlockSectionHeading(
        text=[
            RichTextCustomEmoji(custom_emoji_id=emoji_id, alternative_text=fallback),
            f" Расписание на {weekday}",
        ],
        size=size,
    )


def schedule_table(day_lessons) -> InputRichBlockTable:
    cells = [[make_cell("Время", True), make_cell("Урок", True), make_cell("Кабинет", True)]]
    for lesson in day_lessons:
        cells.append([make_cell(lesson.time or "-"), make_cell(lesson.lesson or "-"), make_cell(str(lesson.cabinet))])
    return InputRichBlockTable(is_bordered=True, is_striped=True, cells=cells)


@router.message(Command("week"))
@router.message(F.text == BTN_WEEK)
async def sent_schedule_week(message: Message) -> None:
    schedule = await get_latest_schedule_week()
    if schedule is not None:
        for element in schedule:
            rich_msg = InputRichMessage(
                blocks=[
                    emoji_heading(element.weekday, "calendar_september_1"),
                    schedule_table(element.lessons),
                ]
            )
            await message.answer_rich(rich_message=rich_msg)


@router.message(Command("today"))
@router.message(F.text == BTN_TODAY)
async def sent_schedule_today(message: Message, state: FSMContext) -> None:
    weekday = datetime.now().weekday()

    week_schedule = await get_latest_schedule_week()
    if not isinstance(week_schedule, list):
        await message.answer("⚠️ Не удалось получить расписание, попробуйте позже")
        return None

    schedule = find_day(week_schedule, weekday)
    if schedule is None:
        await message.answer("📭 На сегодня расписания нет")
        return None

    rich_msg = InputRichMessage(
        blocks=[
            emoji_heading(schedule.weekday, "alarm_clock"),
            schedule_table(schedule.lessons),
        ]
    )
    await message.answer_rich(rich_message=rich_msg)
    await add_data(chatid=message.chat.id, tg_id=message.from_user.id, schedule=week_schedule)


async def scheduled_msg(bot: Bot) -> None:
    weekday = datetime.now().weekday()

    week_schedule = await get_latest_schedule_week()
    if not isinstance(week_schedule, list):
        return None

    schedule = find_day(week_schedule, weekday)
    if schedule is None:
        return None

    today_dict = asdict(schedule)

    rich_msg = InputRichMessage(
        blocks=[
            emoji_heading(schedule.weekday, "bell_gold_ribbon_1"),
            schedule_table(schedule.lessons),
        ]
    )

    for data in await get_all_data():
        past_lessons = find_day_dict(data.last_schedule, weekday) if data.last_schedule is not None else None
        if past_lessons == today_dict:
            continue
        await bot.send_rich_message(chat_id=data.chat_id, rich_message=rich_msg)
        await add_lessons(data.tg_id, week_schedule)


def make_cell(text: str, is_header: bool = False) -> RichBlockTableCell:
    return RichBlockTableCell(
        align="left",
        valign="top",
        text=text,
        is_header=is_header
    )

scheduler.add_job(scheduled_msg, IntervalTrigger(seconds=10), args=[bot])
