from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Bot, Router
from aiogram.fsm.storage.base import StorageKey
from tg.tg_bot_init import bot, dp
from service import add_data, get_data_id
from client import get_latest_schedule_week
from random import randint


scheduler = AsyncIOScheduler()

router = Router()

@router.message(Command("test"))
async def send_msg(message: Message, state: FSMContext) -> None:
    sent = await message.answer("тест 1")
    msgid = sent.message_id
    chatid = sent.chat.id  
    tg_id: int = message.from_user.id
    schedule = await get_latest_schedule_week()
    if (tg_id is not None) and (schedule is not None):
        await add_data(msgid, chatid, tg_id, schedule)
    



async def scheduled_msg(bot: Bot, tg_id: int) -> None:
    data = await get_data_id(tg_id)
    if data is not None:
        sent = await bot.edit_message_text(chat_id=data.chat_id, message_id=data.msg_id, text=str(randint(1, 9999)))
        

scheduler.add_job(scheduled_msg, IntervalTrigger(minutes=1), args=[bot, 8566501752])



    

  