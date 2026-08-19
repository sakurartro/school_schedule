import asyncio
import os

from ai.ai_service import parse_schedule_ai
from data_content import DaySchedule, WeekParsing
from table_to_python import FileWork
from yandex_download import YandexDiskParsing

TABLES_DIR = "tables"
os.makedirs(TABLES_DIR, exist_ok=True)


def table_path(tg_id: int) -> str:
    return f"{TABLES_DIR}/{tg_id}.xlsx"


async def get_latest_schedule_week(
    tg_id: int, table_link: str, grade: str, class_letter: str | None = None
) -> list[DaySchedule] | None:
    file_path = table_path(tg_id)

    downloader = YandexDiskParsing(table_link, file_path=file_path)
    if not await downloader.download_data() and not os.path.exists(file_path):
        return None

    calamine = FileWork(file_path)

    raw_data: list | None = await asyncio.to_thread(calamine.get_raw_data, grade)
    if not raw_data:
        return None

    parser = WeekParsing(raw_data)
    known_letters = parser.class_letters()
    if class_letter and known_letters and class_letter.upper() not in known_letters:
        # Литера пропала из таблицы (её переименовали/убрали) — это не "непонятный
        # формат", тут нечего разбирать через AI: он всё равно бы что-то придумал,
        # подсунув чужой класс. Честно сообщаем, что нужно перевыбрать класс.
        return None

    latest_schedule = parser.parse_table_week(class_letter)

    if not latest_schedule:
        latest_schedule = await parse_schedule_ai(raw_data, class_letter)

    return latest_schedule
