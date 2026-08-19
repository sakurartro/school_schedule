from dataclasses import asdict

from sqlalchemy import select

from connection import async_session
from data_content import DaySchedule
from models import LastInfo


async def save_schedule(chatid: int, tg_id: int, schedule: list[DaySchedule]) -> None:
    """Запоминаем последнее показанное расписание — по нему рассылка ищет изменения."""
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        schedule_data = [asdict(day) for day in schedule]
        if result:
            result.last_schedule = schedule_data
        else:
            session.add(LastInfo(tg_id=tg_id, chat_id=chatid, last_schedule=schedule_data))
        await session.commit()


async def add_user_link(chatid: int, tg_id: int, table_link: str, grade: str, file_path: str) -> None:
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        if result:
            result.chat_id = chatid
            result.table_link = table_link
            result.grade = grade
            result.file_path = file_path
            result.last_schedule = None
        else:
            session.add(
                LastInfo(
                    tg_id=tg_id,
                    chat_id=chatid,
                    table_link=table_link,
                    grade=grade,
                    file_path=file_path,
                )
            )
        await session.commit()


async def get_data_id(tg_id: int) -> LastInfo | None:
    async with async_session() as session:
        return await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))


async def get_all_data() -> list[LastInfo]:
    async with async_session() as session:
        result = await session.scalars(select(LastInfo))
        return list(result)


async def change_grade(tg_id: int, grade: str) -> None:
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        if result:
            result.grade = grade
            result.last_schedule = None
            await session.commit()


async def delete_profile(tg_id: int) -> None:
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        if result:
            await session.delete(result)
            await session.commit()
