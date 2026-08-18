from google import genai
from dotenv import load_dotenv
import json
import ai.prompts
from data_content import Lesson, DaySchedule

load_dotenv()

async def parse_schedule_ai(raw_data: list) -> list[DaySchedule] | None:
    client = genai.Client()

    response = await client.aio.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=ai.prompts.schedule_parse(raw_data),
    )

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

    days: list[DaySchedule] = []
    for day in data:
        lessons = [
            Lesson(
                cabinet=lesson.get("cabinet"),
                lesson=lesson.get("lesson"),
                time=lesson.get("time"),
            )
            for lesson in day.get("lessons", [])
        ]
        days.append(DaySchedule(weekday=day.get("weekday"), lessons=lessons))

    return days
