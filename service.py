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


async def add_user_link(chatid: int, tg_id: int, table_link: str, grade: str, file_path: str) -> None:
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        if result:
            result.table_link = table_link
            await session.commit()
            return None
        new_data = LastInfo(tg_id=tg_id, chat_id=chatid, table_link=table_link, grade=grade, file_path=file_path)
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


async def get_grade_id(tg_id: int):
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        if result:
            print(result.grade)
            return result.grade


async def change_grade(tg_id: int, grade: str) -> None:
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        if result:
            result.grade = grade
            await session.commit()
            return


async def change_table_url(tg_id: int, link: str) -> None:
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        if result:
            result.table_link = link
            await session.commit()
            return


async def delete_profile(tg_id: int) -> None:
    async with async_session() as session:
        result = await session.scalar(select(LastInfo).where(LastInfo.tg_id == tg_id))
        if result:
            await session.delete(result)
            await session.commit()