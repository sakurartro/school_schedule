import re
from dataclasses import dataclass

weekdays: list = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]

# Заголовок литеры в шапке листа: "8 А класс", "5А класс", "10 Б класс" и т.п.
LETTER_CLASS_RE = re.compile(r"([А-ЯЁ])\s*класс", re.IGNORECASE)


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


def _find_header(raw_data: list[list]) -> tuple[int, int]:
    """(строка, колонка) ячейки "Время" — опорной точки шапки таблицы."""
    for row_idx, row in enumerate(raw_data[:3]):
        for col_idx, cell in enumerate(row):
            if isinstance(cell, str) and cell.strip() == "Время":
                return row_idx, col_idx
    return 0, 2


def find_class_letters(raw_data: list[list]) -> dict[str, int]:
    """Литера класса -> индекс колонки "Предмет" для неё.

    Некоторые школы держат параллели (8А/8Б/8В) не отдельными листами,
    а колонками одного листа: в строке с "Время" после неё идут блоки
    "8 А класс" / "8 Б класс" / ... — колонка блока и есть начало пары
    (Предмет, Кабинет) для этой литеры. Если такого деления нет, словарь пуст.
    """
    header_row_idx, time_col = _find_header(raw_data)
    if header_row_idx >= len(raw_data):
        return {}

    letters: dict[str, int] = {}
    header_row = raw_data[header_row_idx]
    for col_idx in range(time_col + 1, len(header_row)):
        cell = header_row[col_idx]
        if not isinstance(cell, str):
            continue
        match = LETTER_CLASS_RE.search(cell)
        if match:
            letters.setdefault(match.group(1).upper(), col_idx)
    return letters


class WeekParsing:
    def __init__(self, raw_data: list[list]):
        self.raw_data = raw_data
        self._header_row, self._time_col = _find_header(raw_data)

    def __str__(self) -> str:
        return f"WeekParsing(raw_data={self.raw_data!r})"

    def class_letters(self) -> list[str]:
        """Литеры классов, найденные в шапке листа, в порядке слева направо."""
        return list(find_class_letters(self.raw_data))

    def parse_table_week(self, letter: str | None = None) -> list[DaySchedule]:
        letters = find_class_letters(self.raw_data)
        if letter and letters:
            letter = letter.strip().upper()
            if letter not in letters:
                # Литера пропала из таблицы (её переименовали/убрали) — лучше
                # честно вернуть пусто и дать AI-фолбэку попытаться разобраться,
                # чем молча показать чужой класс.
                return []
            lesson_col = letters[letter]
        else:
            lesson_col = self._time_col + 1
        cabinet_col = lesson_col + 1

        all_days: list[DaySchedule] = []
        current_day: str | None = None
        current_lessons: list[Lesson] = []

        for row in self.raw_data:
            first_cell = next((cell for cell in row[:2] if cell in weekdays), None)
            if first_cell:
                if current_day:
                    all_days.append(DaySchedule(weekday=current_day, lessons=current_lessons))
                    current_lessons = []
                current_day = first_cell

            if current_day and len(row) > cabinet_col:
                lesson_obj = Lesson(
                    cabinet=clean_cell(row[cabinet_col]),
                    lesson=clean_cell(row[lesson_col]),
                    time=clean_cell(row[self._time_col]),
                )
                current_lessons.append(lesson_obj)
        if current_day:
            all_days.append(DaySchedule(weekday=current_day, lessons=current_lessons))
        return all_days
