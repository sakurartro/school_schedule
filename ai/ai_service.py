from google import genai
from dotenv import load_dotenv
import os
import ai.prompts

load_dotenv()

async def parse_list_dict(file_path: str, grade: str) -> dict | None:
    client = genai.Client()

    response =  client.aio.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents
    )
