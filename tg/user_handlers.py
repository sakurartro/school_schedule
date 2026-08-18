from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from service import get_data_id, delete_profile
from aiogram.enums import ParseMode
import tg.keyboard as kb

router = Router()

class Redirict(StatesGroup):
    redirict = State()

@router.message(Command("profile"))
async def show_profile(message: Message) -> None:
    tg_id = message.from_user.id
    data = await get_data_id(tg_id)
    if data is None:
        await message.answer("Ваш профиль пуст⚠️")
        return
    text = f"""
<tg-emoji emoji-id=\"5350781673103453057\">🔐</tg-emoji>Профиль - {message.from_user.first_name}
<tg-emoji emoji-id=\"5271604874419647061\">🔗</tg-emoji>Расписание - {data.table_link}
<tg-emoji emoji-id=\"5350809912513424561\">🔊</tg-emoji>Класс - {data.grade}\n
<tg-emoji emoji-id=\"5420323339723881652\">⚠️</tg-emoji>Если вы хотите удалить свой аккаунт нажмите /delete
    """
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=await kb.info_kb())


@router.message(Command("delete"))
async def delete_profile_msg(message: Message) -> None:
    await message.answer("<tg-emoji emoji-id=\"5420323339723881652\">⚠️</tg-emoji>Вы точно хотите удалить ваш профиль?", parse_mode=ParseMode.HTML, reply_markup=await kb.delete_kb())


@router.callback_query(F.data == "yes")
async def delete_profile_func(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await delete_profile(callback.from_user.id)
    await callback.message.edit_text("Профиль успешно удален!")
    await state.set_state(Redirict.redirict)

