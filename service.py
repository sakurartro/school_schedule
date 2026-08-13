from dataclasses import asdict
from sqlalchemy import select, delete
from connection import async_session
from data_content import DaySchedule
from models import LastInfo


async def add_data(msgid: int, chatid: int, tg_id: int, schedule: DaySchedule | list[DaySchedule]) -> None:
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        if result:
            return None
        if isinstance(schedule, list):
            schedule_data = [asdict(day) for day in schedule]
        else:
            schedule_data = asdict(schedule)
        new_data = LastInfo(tg_id=tg_id, msg_id=msgid, chat_id=chatid, last_schedule=schedule_data)
        session.add(new_data)
        await session.commit()

async def add_lessons(tg_id, schedule):
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        if result:
            result.last_schedule = schedule
            await session.commit()


async def get_data_id(tg_id: int):
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        return result