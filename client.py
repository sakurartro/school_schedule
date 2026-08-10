from yandex_download import YandexDiskParsing
from data_content import WeekParsing, DaySchedule
from dotenv import load_dotenv
import asyncio
from table_to_python import get_raw_data
from datetime import datetime
import os

load_dotenv()

PUBLIC_KEY: str = os.getenv("TABLE_LINK", "")

async def get_latest_schedule_week() -> list[DaySchedule] | None:
    downloader: YandexDiskParsing = YandexDiskParsing(PUBLIC_KEY)

    is_updated: bool = await downloader.update_data()

    if not is_updated:
        return None

    raw_data: list = await asyncio.to_thread(get_raw_data)

    schedule: WeekParsing = WeekParsing(raw_data)

    latest_schedule: list = schedule.parse_table_week()

    return latest_schedule


async def get_latest_schedule_day() -> DaySchedule | None:
    day_num = datetime.now().weekday()
    downloader = YandexDiskParsing(PUBLIC_KEY)

    is_updated = await downloader.update_data()

    if not is_updated:
        return None

    raw_data = await asyncio.to_thread(get_raw_data)

    schedule = WeekParsing(raw_data)

    latest_schedule: list = schedule.parse_table_week()

    

    today_data = latest_schedule[day_num]

    return today_data



if __name__ == "__main__":
    print(asyncio.run(get_latest_schedule_day()))





    
