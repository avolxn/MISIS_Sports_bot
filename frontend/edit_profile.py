from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from backend.db import get_userdata, update_userdata
from frontend.text import *
import re

router = Router()

class EditProfile(StatesGroup):
    edit_name = State()
    edit_lastname = State()
    edit_studentid = State()
    edit_language = State()

@router.callback_query(lambda callback: callback.data == "edit_profile")
async def edit_profile(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await get_userdata(telegram_id=callback.from_user.id)
    is_english = int(data.is_english)
    
    buttons = InlineKeyboardBuilder()
    buttons.row(
        types.InlineKeyboardButton(
            text=EDIT_NAME[is_english],
            callback_data="edit_name")
    )
    buttons.row(
        types.InlineKeyboardButton(
            text=EDIT_LASTNAME[is_english],
            callback_data="edit_lastname")
    )
    buttons.row(
        types.InlineKeyboardButton(
            text=EDIT_STUDENTID[is_english],
            callback_data="edit_studentid")
    )
    buttons.row(
        types.InlineKeyboardButton(
            text=EDIT_LANGUAGE[is_english],
            callback_data="edit_language")
    )
    await callback.message.answer(EDIT_PROFILE[is_english], reply_markup=buttons.as_markup())
    await callback.answer()
