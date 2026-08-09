from python_calamine import CalamineWorkbook
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

GRADE: str = os.getenv("DEFAULT_GRADE", "8 класс")

def get_raw_data():
    wb = CalamineWorkbook.from_path("table.xlsx")
    ws = wb.get_sheet_by_name(GRADE)
    return ws.to_python()

