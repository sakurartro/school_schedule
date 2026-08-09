from aiogram.types import Message, CallbackQuery, InputRichMessage, InputRichBlock, InputRichBlockSectionHeading, InputRichBlockTable, RichBlockTableCell
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from client import get_latest_schedule


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(f"Привет {message.from_user.first_name}")


@router.message(Command("schedule"))
async def sent_schedule(message: Message) -> None:
    schedule = await get_latest_schedule()

    if schedule is not None:
        for element in schedule:
            day_lessons = element.lessons
            weekday = element.weekday
            cells = [[make_cell("Время", True), make_cell("Урок", True), make_cell("Кабинет", True)]]
            for lesson in day_lessons:
                cells.append([make_cell(lesson.time or "-"), make_cell(lesson.lesson or "-"), make_cell(str(lesson.cabinet))])

            rich_msg = InputRichMessage(
                blocks=[
                    InputRichBlockSectionHeading(text=f"Расписание", size=2),
                    InputRichBlockTable(is_bordered=True, is_striped=True, cells=cells)
                ]
            )

            await message.answer_rich(rich_message=rich_msg)
            
def make_cell(text: str, is_header: bool = False) -> RichBlockTableCell:
    return RichBlockTableCell(
        align="left",
        valign="top",
        text=text,
        is_header=is_header
    )