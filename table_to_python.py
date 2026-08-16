from python_calamine import CalamineWorkbook
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

GRADE: str = os.getenv("DEFAULT_GRADE", "8 класс")

def get_raw_data(file_path: str = "table.xlsx"):
    wb = CalamineWorkbook.from_path(file_path)
    ws = wb.get_sheet_by_name(GRADE)
    return ws.to_python()


def main():
    print(get_raw_data())


if __name__ == "__main__":
    main()
