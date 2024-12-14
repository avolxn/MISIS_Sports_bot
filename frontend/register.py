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
    """
    В начале спрашиваем у пользователя язык
    Args:
        message (types.Message): Сообщение, отправленное пользователем.
        state (FSMContext): Машина состояний
    Returns: None
    """
    kb = [
        [types.KeyboardButton(text="🇬🇧 English")],
        [types.KeyboardButton(text="🇷🇺 Русский")],
        [types.KeyboardButton(text="🇩🇪 Deutsch")],
        [types.KeyboardButton(text="🇸🇦 العربية")],
        [types.KeyboardButton(text="🇮🇱 עברית")],
        [types.KeyboardButton(text="🤖 01000010 01101001 01101110 01100001 01110010 01111001")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await message.answer(CHOOSE_LANGUAGE, reply_markup=keyboard)
    await state.set_state(User.last_name)
    
@router.message(User.last_name)
async def language_chosen(message: types.Message, state: FSMContext) -> None:
    """
    Спрашиваем фамилию, затем в следующих функциях имя и студ.билет.
    Есть проверка на корректность данных.
    Args:
        message (types.Message): Сообщение, отправленное пользователем.
        state (FSMContext): Машина состояний
    Returns: None
    """
    if not message.text in LANGUAGES:
        await message.answer(CHOOSE_LANGUAGE)
        return
    await state.update_data(language=LANGUAGES.index(message.text))
    data = await state.get_data()
    await message.answer(WHATS_LASTNAME[data['language']], reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(User.first_name)

# Получение фамилии
@router.message(User.first_name)
async def lastname_chosen(message: types.Message, state: FSMContext) -> None:
    """документацию см. в language_chosen"""
    data = await state.get_data()
    if not re.match(r'^[А-Яа-яЁё]+(?:[- ]?[А-Яа-яЁё]+)*$', message.text):
        await message.answer(ERROR_LASTNAME[data['language']])
        return
    await state.update_data(last_name=message.text.title())
    language = int(data.get('language', False))
    await message.answer(WHATS_FIRSTNAME[language])
    await state.set_state(User.student_id)

# Получение имени
@router.message(User.student_id)
async def first_name_chosen(message: types.Message, state: FSMContext) -> None:
    """документацию см. в language_chosen"""
    data = await state.get_data()
    if not re.match(r'^[А-Яа-яЁё]+(?:[- ]?[А-Яа-яЁё]+)*$', message.text):
        await message.answer(ERROR_FIRSTNAME[data['language']])
        return
    await state.update_data(first_name=message.text.title())
    language = int(data.get('language', False))
    await message.answer(WHATS_STUDENTID[language])
    await state.set_state(User.reg_finished)

# Получение ID и завершение регистрации
@router.message(User.reg_finished)
async def student_id_chosen(message: types.Message, state: FSMContext) -> None:
    """
    Проверяем номер студ. билета
    После этого в базе данных создаем нового пользователя. 
    Можно смело записываться на пары.
    """
    data = await state.get_data()
    language = int(data.get('language', False))
    if not re.match(r'^\d{7}$', message.text):
        await message.answer(ERROR_STUDENTID[language])
        return
    data = await state.get_data()
    # Регистрируем студента
    await register_student(
        telegram_id=message.from_user.id,
        last_name=data['last_name'],
        first_name=data['first_name'],
        student_id=message.text,
        language=data['language']
    )
    # Сообщение о завершении регистрации
    await message.answer(REGISTERED_SUCCESSFULLY[data['language']])
    await state.clear()
    await state.set_data(data)
