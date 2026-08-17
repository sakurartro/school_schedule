
from dataclasses import dataclass
import asyncio

weekdays: list = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]


@dataclass
class Lesson:
    cabinet: int | str | None = None
    lesson: str | None = None
    time: str | None = None


@dataclass
class DaySchedule:
    weekday: str
    lessons: list[Lesson]


def find_day(days: list[DaySchedule], weekday_index: int) -> DaySchedule | None:
    name = weekdays[weekday_index]
    for day in days:
        if day.weekday == name:
            return day
    return None


def find_day_dict(days: list[dict], weekday_index: int) -> dict | None:
    name = weekdays[weekday_index]
    for day in days:
        if day.get("weekday") == name:
            return day
    return None


class WeekParsing:
    def __init__(self, raw_data: list[list]):
        self.schedule: list[DaySchedule]
        self.raw_data = raw_data

    def __str__(self) -> str:
        return f"WeekParsing(raw_data={self.raw_data!r})"

    def _find_time_column(self) -> int:
        for row in self.raw_data[:3]:
            for idx, cell in enumerate(row):
                if isinstance(cell, str) and cell.strip() == "Время":
                    return idx
        return 2

    def parse_table_week(self) -> list[DaySchedule]:
        all_days: list[DaySchedule] = []
        current_day: str | None = None
        current_lessons: list[Lesson] = []
        time_col = self._find_time_column()

        for row in self.raw_data:
            first_cell = next((cell for cell in row[:2] if cell in weekdays), None)
            if first_cell:
                if current_day:
                    all_days.append(DaySchedule(weekday=current_day, lessons=current_lessons))
                    current_lessons = []
                current_day = first_cell

            if current_day and len(row) > time_col + 2:
                time_row = row[time_col]
                lesson_row = row[time_col + 1]
                cabinet_row = row[time_col + 2]
                if isinstance(cabinet_row, float):
                    cabinet_row = int(cabinet_row)
                time_value = str(time_row).replace("\xa0", "").strip() if time_row else "-"
                lesson = str(lesson_row).replace("\xa0", "").strip() if lesson_row else "-"
                cabinet = str(cabinet_row).replace("\xa0", "").strip() if cabinet_row else "-"
                lesson_obj = Lesson(
                    cabinet=cabinet,
                    lesson=lesson,
                    time=time_value
                )
                current_lessons.append(lesson_obj)
        if current_day:
            all_days.append(DaySchedule(weekday=current_day, lessons=current_lessons))
        return all_days


