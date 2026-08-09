from table_to_python import get_raw_data
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


class WeekParsing:
    def __init__(self, raw_data: list[list]):
        self.schedule: list[DaySchedule]
        self.raw_data = raw_data

    def __str__(self) -> str:
        return f"WeekParsing(raw_data={self.raw_data!r})"

    def parse_table(self) -> list[DaySchedule]:
        all_days: list[DaySchedule] = []
        current_day: str | None = None
        current_lessons: list[Lesson] = []

        for row in self.raw_data:
            first_cell = row[0]
            if first_cell in weekdays:
                if current_day:
                    all_days.append(DaySchedule(weekday=current_day, lessons=current_lessons))
                    current_lessons = []
                current_day = first_cell

            elif len(row) > 3:
                cabinet_row = row[4] if len(row) > 4 else None
                if isinstance(cabinet_row, float):
                    cabinet_row = int(cabinet_row)
                lesson_row = row[3] if len(row) > 3 else None
                cabinet = str(cabinet_row).replace("\xa0", "").strip() if cabinet_row else None
                lesson = str(lesson_row).replace("\xa0", "").strip() if lesson_row else None
                lesson_obj = Lesson(
                    cabinet=cabinet,
                    lesson=lesson,
                    time=row[2] if len(row) > 2 else None
                )
                current_lessons.append(lesson_obj)
        if current_day:
            all_days.append(DaySchedule(weekday=current_day, lessons=current_lessons))
        return all_days

async def main():
    raw_data = await asyncio.to_thread(get_raw_data)
    schedule = WeekParsing(raw_data)
    valids = schedule.parse_table()
    print(valids)


if __name__ == "__main__":
    asyncio.run(main())

    
