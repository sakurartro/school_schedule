from aiogram.types import (
    Message,
    InputRichMessage
)
from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from client import get_latest_schedule_week
from service import add_data, get_data_id
from data_content import find_day
from datetime import datetime
import tg.keyboard as kb
from tg.rich_render import schedule_table_week, emoji_heading
from tg.keyboard import BTN_TODAY, BTN_WEEK, BTN_TOMMOROW


router = Router()



@router.message(Command("week"))
@router.message(F.text == BTN_WEEK)
async def sent_schedule_week(message: Message) -> None:
    user = await get_data_id(message.from_user.id)
    if user is None or not user.table_link:
        await message.answer("⚠️ Сначала пришли ссылку на таблицу через /start")
        return None

    schedule = await get_latest_schedule_week(message.from_user.id, user.table_link)
    if schedule is not None:
        rich_msg = InputRichMessage(
            blocks=[
                emoji_heading("на неделю", "calendar_september_1"),
                schedule_table_week(schedule),
            ]
        )
        await message.answer_rich(rich_msg, reply_markup=await kb.info_kb())


@router.message(Command("today"))
@router.message(Command("tomorrow"))
@router.message(F.text == BTN_TOMMOROW)
@router.message(F.text == BTN_TODAY)
async def sent_schedule_today(message: Message, state: FSMContext) -> None:
    istoday: bool = False
    if message.text in [BTN_TODAY, "/today"]:
        weekday = datetime.now().weekday()
        istoday = True

    elif message.text in [BTN_TOMMOROW, "/tomorrow"]:
        weekday = (datetime.now().weekday()) + 1
    user = await get_data_id(message.from_user.id)
    if user is None or not user.table_link:
        await message.answer("⚠️ Сначала пришли ссылку на таблицу через /start")
        return None

    week_schedule = await get_latest_schedule_week(
        message.from_user.id, user.table_link
    )
    if not isinstance(week_schedule, list):
        await message.answer("⚠️ Не удалось получить расписание, попробуйте позже")
        return None

    schedule = find_day(week_schedule, weekday)
    if schedule is None:
        if istoday:
            await message.answer("📭 На сегодня расписания нет")
        else:
            await message.answer("📭 На завтра расписания нет")
        return None

    rich_msg = InputRichMessage(
        blocks=[
            emoji_heading(schedule.weekday, "alarm_clock"),
            schedule_table_week([schedule]),
        ]
    )
    await message.answer_rich(rich_message=rich_msg, reply_markup=await kb.info_kb())
    await add_data(
        chatid=message.chat.id, tg_id=message.from_user.id, schedule=week_schedule
    )




            

