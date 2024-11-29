from aiogram import types
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from .text import *
from backend.cors import *

router = Router()

# Машина состояний
class User(StatesGroup):
    last_name = State()
    first_name = State()
    student_id = State()
    reg_finished = State()

# Начало регистрации
@router.message(User.last_name)
async def reg_start(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    await message.answer(WHATS_LASTNAME[data['is_english']])
    await state.set_state(User.first_name)

# Получение фамилии
@router.message(User.first_name)
async def lastname_chosen(message: types.Message, state: FSMContext) -> None:
    await state.update_data(last_name=message.text)
    data = await state.get_data()
    await message.answer(WHATS_FIRSTNAME[data['is_english']])
    await state.set_state(User.student_id)

# Получение имени
@router.message(User.student_id)
async def first_name_chosen(message: types.Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text)
    data = await state.get_data()
    await message.answer(WHATS_STUDENTID[data['is_english']])
    await state.set_state(User.reg_finished)

# Получение ID и завершение регистрации
@router.message(User.reg_finished)
async def student_id_chosen(message: types.Message, state: FSMContext) -> None:
    await state.update_data(student_id=message.text)
    await state.update_data(is_english=False)
    await state.update_data(points=0)
    userdata = await state.get_data()
    
    # Регистрируем студента
    await register_student(
        telegram_id=message.from_user.username,
        last_name=userdata['last_name'],
        first_name=userdata['first_name'],
        student_id=userdata['student_id']
    )

    # Сообщение о завершении регистрации
    await message.answer(
        REGISTERED_SUCCESSFULLY[userdata['is_english']] + f"\n"
        f"{userdata['last_name']} {userdata['first_name']} ({userdata['student_id']})"
    )
    await state.clear()
    await state.set_data(userdata)
