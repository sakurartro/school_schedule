from dataclasses import asdict
from sqlalchemy import select, delete
from connection import async_session
from data_content import DaySchedule
from models import LastInfo


async def add_data(chatid: int, tg_id: int, schedule: list[DaySchedule]) -> None:
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        schedule_data = [asdict(day) for day in schedule]
        if result:
            if result.last_schedule is None:
                result.last_schedule = schedule_data
                await session.commit()
            return None
        new_data = LastInfo(tg_id=tg_id, chat_id=chatid, last_schedule=schedule_data)
        session.add(new_data)
        await session.commit()


async def add_user_link(chatid: int, tg_id: int, table_link: str) -> None:
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        if result:
            result.table_link = table_link
            await session.commit()
            return None
        new_data = LastInfo(tg_id=tg_id, chat_id=chatid, table_link=table_link)
        session.add(new_data)
        await session.commit()

async def add_lessons(tg_id: int, schedule: list[DaySchedule]) -> None:
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        if result:
            result.last_schedule = [asdict(day) for day in schedule]
            await session.commit()


async def get_data_id(tg_id: int):
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        return result


async def get_all_data() -> list[LastInfo]:
    async with async_session() as session:
        result = await session.scalars(select(LastInfo))
        return list(result)