from dataclasses import dataclass

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


def clean_cell(value) -> str:
    """Ячейка в читаемый вид: числа без .0, без неразрывных пробелов, пустое — прочерк."""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    text = str(value).replace("\xa0", "").strip() if value else ""
    return text or "-"


def find_day(days: list[DaySchedule], weekday_index: int) -> DaySchedule | None:
    name = weekdays[weekday_index % len(weekdays)]
    for day in days:
        if day.weekday == name:
            return day
    return None


def find_day_dict(days: list[dict], weekday_index: int) -> dict | None:
    name = weekdays[weekday_index % len(weekdays)]
    for day in days:
        if day.get("weekday") == name:
            return day
    return None


class WeekParsing:
    def __init__(self, raw_data: list[list]):
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
                lesson_obj = Lesson(
                    cabinet=clean_cell(row[time_col + 2]),
                    lesson=clean_cell(row[time_col + 1]),
                    time=clean_cell(row[time_col]),
                )
                current_lessons.append(lesson_obj)
        if current_day:
            all_days.append(DaySchedule(weekday=current_day, lessons=current_lessons))
        return all_days
