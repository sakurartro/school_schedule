import json
import logging
from functools import lru_cache

from dotenv import load_dotenv
from google import genai

import ai.prompts
from data_content import DaySchedule, Lesson, weekdays

load_dotenv()

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    return genai.Client()


async def parse_schedule_ai(raw_data: list, class_letter: str | None = None) -> list[DaySchedule] | None:
    try:
        response = await get_client().aio.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=ai.prompts.schedule_parse(raw_data, class_letter),
        )
    except Exception as e:
        logger.warning("Не удалось разобрать расписание через ИИ: %s", e)
        return None

    text = response.text
    if text is None:
        return None

    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json").strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, list):
        return None

    days: list[DaySchedule] = []
    for day in data:
        weekday = day.get("weekday")
        if weekday not in weekdays:
            continue
        lessons = [
            Lesson(
                cabinet=lesson.get("cabinet"),
                lesson=lesson.get("lesson"),
                time=lesson.get("time"),
            )
            for lesson in day.get("lessons", [])
        ]
        days.append(DaySchedule(weekday=weekday, lessons=lessons))

    return days
