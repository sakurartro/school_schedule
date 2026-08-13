from aiogram.types import Message, CallbackQuery, InputRichMessage, InputRichBlock, InputRichBlockSectionHeading, InputRichBlockTable, RichBlockTableCell
from aiogram import F, Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from client import get_latest_schedule_week
from dataclasses import asdict
from tg.tg_bot_init import bot
from service import add_data, get_data_id, add_lessons
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(f"Привет {message.from_user.first_name}")
    

@router.message(Command("week"))
async def sent_schedule_week(message: Message) -> None:
    schedule = await get_latest_schedule_week()
    if schedule is not None:
        for element in schedule:
            day_lessons = element.lessons
            weekday = element.weekday
            cells = [[make_cell("Время", True), make_cell("Урок", True), make_cell("Кабинет", True)]]
            for lesson in day_lessons:
                cells.append([make_cell(lesson.time or "-"), make_cell(lesson.lesson or "-"), make_cell(str(lesson.cabinet))])

            rich_msg = InputRichMessage(
                blocks=[
                    InputRichBlockSectionHeading(text=f"Расписание на {weekday}", size=2),
                    InputRichBlockTable(is_bordered=True, is_striped=True, cells=cells)
                ]
            )

            await message.answer_rich(rich_message=rich_msg)


@router.message(Command("today"))
async def sent_schedule_today(message: Message, state: FSMContext) -> None:
    weekday = datetime.now().weekday()

    week_schedule = await get_latest_schedule_week()
    if isinstance(week_schedule, list):
        schedule = week_schedule[weekday]

    day_lessons = schedule.lessons
    weekday = schedule.weekday
    cells = [[make_cell("Время", True), make_cell("Урок", True), make_cell("Кабинет", True)]]
    for lesson in day_lessons:
        cells.append([make_cell(lesson.time or "-"), make_cell(lesson.lesson or "-"), make_cell(str(lesson.cabinet))])

    rich_msg = InputRichMessage(
        blocks=[
            InputRichBlockSectionHeading(text=f"Расписание на {weekday}", size=2),
            InputRichBlockTable(is_bordered=True, is_striped=True, cells=cells)
        ]
    )
    sent = await message.answer_rich(rich_message=rich_msg)
    msg_id = sent.message_id
    chat_id = sent.chat.id
    tg_id = message.from_user.id
    await add_data(msgid=msg_id, chatid=chat_id, tg_id=tg_id, schedule=schedule)
    

async def scheduled_msg(bot: Bot, tg_id: int) -> None:
    data = await get_data_id(tg_id)
    weekday = datetime.now().weekday()

    past_lessons = None 

    if (data is not None) and (data.last_schedule is not None):
        past_lessons = data.last_schedule
        past_lessons = past_lessons[weekday] 

    
    week_schedule = await get_latest_schedule_week()
    if isinstance(week_schedule, list):
        schedule = week_schedule[weekday]

    if asdict(schedule) == past_lessons:
        return None

    
    day_lessons = schedule.lessons
    weekday = schedule.weekday
    cells = [[make_cell("Время", True), make_cell("Урок", True), make_cell("Кабинет", True)]]
    for lesson in day_lessons:
        cells.append([make_cell(lesson.time or "-"), make_cell(lesson.lesson or "-"), make_cell(str(lesson.cabinet))])

    rich_msg = InputRichMessage(
        blocks=[
            InputRichBlockSectionHeading(text=f"Расписание на {weekday}", size=2),
            InputRichBlockTable(is_bordered=True, is_striped=True, cells=cells)
        ]
    )
    
    if data is not None:
        sent = await bot.edit_message_text(chat_id=data.chat_id, message_id=data.msg_id, rich_message=rich_msg)
        await add_lessons(tg_id, week_schedule)

         
def make_cell(text: str, is_header: bool = False) -> RichBlockTableCell:
    return RichBlockTableCell(
        align="left",
        valign="top",
        text=text,
        is_header=is_header
    )

scheduler.add_job(scheduled_msg, IntervalTrigger(seconds=10), args=[bot, 8566501752])




