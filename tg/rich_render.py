from datetime import datetime

from aiogram.types import (
    InputRichBlockSectionHeading,
    InputRichBlockTable,
    RichBlockTableCell,
    RichTextCustomEmoji,
)

from config import SCHOOL_EMOJI
from data_content import DaySchedule, weekdays
from tg.keyboard import SCHOOL_TZ


def schedule_table_week(days_lessons: list[DaySchedule]) -> InputRichBlockTable:
    today = weekdays[datetime.now(tz=SCHOOL_TZ).weekday()]

    day_names_row = []
    header_row = []
    for day in days_lessons:
        label = f"📍 {day.weekday}" if day.weekday == today else day.weekday
        day_names_row.append(make_cell(label, True, colspan=3))
        header_row.extend(
            [
                make_cell("Время", True),
                make_cell("Урок", True),
                make_cell("Кабинет", True),
            ]
        )
    cells = [day_names_row, header_row]

    max_lessons = max((len(day.lessons) for day in days_lessons), default=0)

    for cur_lesson in range(max_lessons):
        row = []
        for day in days_lessons:
            if cur_lesson < len(day.lessons):
                lesson = day.lessons[cur_lesson]
                row.extend(
                    [
                        make_cell(lesson.time or "-"),
                        make_cell(lesson.lesson or "-"),
                        make_cell(str(lesson.cabinet or "-")),
                    ]
                )
            else:
                row.extend([make_cell("-"), make_cell("-"), make_cell("-")])
        cells.append(row)

    return InputRichBlockTable(is_bordered=True, is_striped=True, cells=cells)


def make_cell(
    text: str, is_header: bool = False, colspan: int | None = None
) -> RichBlockTableCell:
    return RichBlockTableCell(
        align="left",
        valign="top",
        text=text,
        is_header=is_header,
        colspan=colspan,
    )


def emoji_heading(
    weekday: str, emoji_key: str, size: int = 2
) -> InputRichBlockSectionHeading:
    emoji_id, fallback = SCHOOL_EMOJI[emoji_key]
    return InputRichBlockSectionHeading(
        text=[
            RichTextCustomEmoji(custom_emoji_id=emoji_id, alternative_text=fallback),
            f" Расписание на {weekday}",
        ],
        size=size,
    )
