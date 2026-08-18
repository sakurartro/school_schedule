from python_calamine import CalamineWorkbook
import asyncio
import os
from dotenv import load_dotenv
from service import get_grade_id

load_dotenv()


class FileWork:
    def __init__(self, file_path: str, tg_id: int) -> None:
        self.file_path = file_path
        self.tg_id = tg_id

    def get_raw_data(self) -> list | None:
        GRADE = asyncio.run(get_grade_id(self.tg_id))
        if GRADE is None:
            return None
        wb = CalamineWorkbook.from_path(self.file_path)
        sheet_name = next(
            (name for name in wb.sheet_names if name.strip() == GRADE.strip()),
            None,
        )
        if sheet_name is None:
            return None
        ws = wb.get_sheet_by_name(sheet_name)
        return ws.to_python()

    def get_all_sheets(self):
        wb = CalamineWorkbook.from_path(self.file_path)
        return wb.sheet_names







def main():
    print(get_raw_data())


if __name__ == "__main__":
    main()
