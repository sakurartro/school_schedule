from yandex_download import YandexDiskParsing
from data_content import WeekParsing, DaySchedule
import asyncio
import os
from table_to_python import get_raw_data

TABLES_DIR = "tables"
os.makedirs(TABLES_DIR, exist_ok=True)


async def get_latest_schedule_week(tg_id: int, table_link: str) -> list[DaySchedule] | None:
    file_path = f"{TABLES_DIR}/{tg_id}.xlsx"

    downloader: YandexDiskParsing = YandexDiskParsing(table_link, file_path=file_path)
    await downloader.download_data()

    raw_data: list = await asyncio.to_thread(get_raw_data, file_path)

    schedule: WeekParsing = WeekParsing(raw_data)

    latest_schedule: list = schedule.parse_table_week()

    return latest_schedule
