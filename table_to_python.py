from python_calamine import CalamineWorkbook


class FileWork:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def _open(self) -> CalamineWorkbook | None:
        try:
            return CalamineWorkbook.from_path(self.file_path)
        except (OSError, ValueError):
            return None

    def get_raw_data(self, grade: str) -> list | None:
        wb = self._open()
        if wb is None:
            return None
        sheet_name = next(
            (name for name in wb.sheet_names if name.strip() == grade.strip()),
            None,
        )
        if sheet_name is None:
            return None
        ws = wb.get_sheet_by_name(sheet_name)
        return ws.to_python()

    def get_all_sheets(self) -> list[str]:
        wb = self._open()
        if wb is None:
            return []
        return wb.sheet_names
