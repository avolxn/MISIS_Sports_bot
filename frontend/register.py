from aiogram import types
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from .text import *
from backend.cors import *
import re

router = Router()

# Машина состояний
class User(StatesGroup):
    language = State()
    last_name = State()
    first_name = State()
    student_id = State()
    reg_finished = State()

# Начало регистрации
@router.message(User.language)
async def reg_start(message: types.Message, state: FSMContext) -> None:
    kb = [
        [types.KeyboardButton(text="🇬🇧 English")],
        [types.KeyboardButton(text="🇷🇺 Русский")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await message.answer(CHOOSE_LANGUAGE, reply_markup=keyboard)
    await state.set_state(User.last_name)
    
@router.message(User.last_name)
async def language_chosen(message: types.Message, state: FSMContext) -> None:
    if not message.text in ['🇬🇧 English', '🇷🇺 Русский']:
        await message.answer(CHOOSE_LANGUAGE)
        return
    await state.update_data(is_english=(message.text=='🇬🇧 English'))
    data = await state.get_data()
    await message.answer(WHATS_LASTNAME[data['is_english']], reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(User.first_name)

# Получение фамилии
@router.message(User.first_name)
async def lastname_chosen(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    if not re.match(r'^[А-Яа-яЁё]+(?:[- ]?[А-Яа-яЁё]+)*$', message.text):
        await message.answer(ERROR_LASTNAME[data['is_english']])
        return
    await state.update_data(last_name=message.text.title())
    is_english = int(data.get('is_english', False))
    await message.answer(WHATS_FIRSTNAME[is_english])
    await state.set_state(User.student_id)

# Получение имени
@router.message(User.student_id)
async def first_name_chosen(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    if not re.match(r'^[А-Яа-яЁё]+(?:[- ]?[А-Яа-яЁё]+)*$', message.text):
        await message.answer(ERROR_FIRSTNAME[data['is_english']])
        return
    await state.update_data(first_name=message.text.title())
    is_english = int(data.get('is_english', False))
    await message.answer(WHATS_STUDENTID[is_english])
    await state.set_state(User.reg_finished)

# Получение ID и завершение регистрации
@router.message(User.reg_finished)
async def student_id_chosen(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    is_english = int(data.get('is_english', False))
    if not re.match(r'^\d{7}$', message.text):
        await message.answer(ERROR_STUDENTID[is_english])
        return
    data = await state.get_data()
    # Регистрируем студента
    await register_student(
        telegram_id=message.from_user.id,
        last_name=data['last_name'],
        first_name=data['first_name'],
        student_id=message.text,
        is_english=data['is_english']
    )
    # Сообщение о завершении регистрации
    await message.answer(REGISTERED_SUCCESSFULLY[data['is_english']])
    await state.clear()
    await state.set_data(data)
