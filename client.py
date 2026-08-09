from yandex_download import YandexDiskParsing
from data_content import WeekParsing, DaySchedule
from dotenv import load_dotenv
import asyncio
from table_to_python import get_raw_data
import os

load_dotenv()

PUBLIC_KEY: str = os.getenv("TABLE_LINK", "")

async def get_latest_schedule() -> list[DaySchedule] | None:
    downloader = YandexDiskParsing(PUBLIC_KEY)

    is_updated = downloader.update_data()

    if not is_updated:
        return None

    raw_data = await asyncio.to_thread(get_raw_data)

    schedule = WeekParsing(raw_data)

    latest_schedule = schedule.parse_table()

    return latest_schedule

    
