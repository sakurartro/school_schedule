from python_calamine import CalamineWorkbook, WorksheetNotFound
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

GRADE: str = os.getenv("DEFAULT_GRADE", "8 класс")


class FileWork:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def get_raw_data(self) -> list | None:
        wb = CalamineWorkbook.from_path(self.file_path)
        try:
            ws = wb.get_sheet_by_name(GRADE)
        except WorksheetNotFound:
            return None
        return ws.to_python()

    def get_all_sheets(self):
        wb = CalamineWorkbook.from_path(self.file_path)
        return wb.sheet_names







def main():
    print(get_raw_data())


if __name__ == "__main__":
    main()
