from yandex_download import YandexDiskParsing
from data_content import WeekParsing, DaySchedule
import asyncio
import os
from table_to_python import FileWork

TABLES_DIR = "tables"
os.makedirs(TABLES_DIR, exist_ok=True)


async def get_latest_schedule_week(tg_id: int, table_link: str, ai: bool = False) -> list[DaySchedule] | None:
    # file_path = f"{TABLES_DIR}/{tg_id}.xlsx"
    file_path = f"tables/demo2.xlsx"

    # downloader: YandexDiskParsing = YandexDiskParsing(table_link, file_path=file_path)
    # await downloader.download_data()

    calamine = FileWork(file_path)

    raw_data: list | None = await asyncio.to_thread(calamine.get_raw_data)
    if raw_data is None:
        return 
    
    schedule: WeekParsing = WeekParsing(raw_data)

    latest_schedule: list = schedule.parse_table_week()

    if latest_schedule == []:
        ...

    return latest_schedule


if __name__ == "__main__":
    print(asyncio.run(get_latest_schedule_week(12, "io", False)))