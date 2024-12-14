from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from backend.cors import *
from .register import *
from frontend.text import *
import re

router = Router()

class EditProfile(StatesGroup):
    edit_firstname = State()
    edit_lastname = State()
    edit_studentid = State()
    edit_language = State()

async def show_edit_profile(language: int):
    buttons = InlineKeyboardBuilder()
    buttons.row(
        types.InlineKeyboardButton(
            text=EDIT_FIRSTNAME[language],
            callback_data="edit_firstname")
    )
    buttons.row(
        types.InlineKeyboardButton(
            text=EDIT_LASTNAME[language],
            callback_data="edit_lastname")
    )
    buttons.row(
        types.InlineKeyboardButton(
            text=EDIT_STUDENTID[language],
            callback_data="edit_studentid")
    )
    buttons.row(
        types.InlineKeyboardButton(
            text=EDIT_LANGUAGE[language],
            callback_data="edit_language")
    )
    return buttons

@router.callback_query(lambda callback: callback.data == "edit_profile")
async def edit_profile(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await get_userdata(telegram_id=callback.from_user.id)
    language = int(data.language)
    keyboard = await show_edit_profile(language)
    await callback.message.edit_text(EDIT_PROFILE[language],
                                     reply_markup=keyboard.as_markup())
    await callback.answer()

#Смена имени
@router.callback_query(lambda callback: callback.data == 'edit_firstname')
async def edit_firstname_request(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await get_userdata(telegram_id=callback.from_user.id)
    language = int(data.language)

    await callback.message.edit_text(WHATS_FIRSTNAME[language])
    await callback.answer()
    await state.set_state(EditProfile.edit_firstname)

@router.message(EditProfile.edit_firstname)
async def edit_firstname_process(message: types.Message, state: FSMContext) -> None:
    data = await get_userdata(telegram_id=message.from_user.id)
    language = int(data.language)

    if not re.match(r'^[А-Яа-яЁё]+(?:[- ]?[А-Яа-яЁё]+)*$', message.text):
        await message.answer(ERROR_FIRSTNAME[language])
        return
    else:
        await update_firstname(telegram_id=message.from_user.id, first_name=message.text.title())
        keyboard = await show_edit_profile(language)
        await message.answer(FIRSTNAME_CHANGED[language])
        await message.answer(EDIT_PROFILE[language], reply_markup=keyboard.as_markup())
        await state.clear()

#Смена фамилии
@router.callback_query(lambda callback: callback.data == 'edit_lastname')
async def edit_lastname_request(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await get_userdata(telegram_id=callback.from_user.id)
    language = int(data.language)

    await callback.message.edit_text(WHATS_LASTNAME[language])
    await callback.answer()
    await state.set_state(EditProfile.edit_lastname)

@router.message(EditProfile.edit_lastname)
async def edit_lastname_process(message: types.Message, state: FSMContext) -> None:
    data = await get_userdata(telegram_id=message.from_user.id)
    language = int(data.language)

    if not re.match(r'^[А-Яа-яЁё]+(?:[- ]?[А-Яа-яЁё]+)*$', message.text):
        await message.answer(ERROR_LASTNAME[language])
        return
    else:
        await update_lastname(telegram_id=message.from_user.id, last_name=message.text.title())
        keyboard = await show_edit_profile(language)
        await message.answer(LASTNAME_CHANGED[language])
        await message.answer(EDIT_PROFILE[language], reply_markup=keyboard.as_markup())
        await state.clear()

#Смена студенческого билета
@router.callback_query(lambda callback: callback.data == 'edit_studentid')
async def edit_studentid_request(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await get_userdata(telegram_id=callback.from_user.id)
    language = int(data.language)
    await callback.message.edit_text(WHATS_STUDENTID[language])
    await callback.answer()
    await state.set_state(EditProfile.edit_studentid)

@router.message(EditProfile.edit_studentid)
async def edit_studentid_process(message: types.Message, state: FSMContext) -> None:
    data = await get_userdata(telegram_id=message.from_user.id)
    language = int(data.language)

    if not re.match(r'^\d{7}$', message.text):
        await message.answer(ERROR_STUDENTID[language])
        return
    else:
        await update_studentid(telegram_id=message.from_user.id, student_id=message.text)
        keyboard = await show_edit_profile(language)
        await message.answer(STUDENTID_CHANGED[language])
        await message.answer(EDIT_PROFILE[language], reply_markup=keyboard.as_markup())
        await state.clear()