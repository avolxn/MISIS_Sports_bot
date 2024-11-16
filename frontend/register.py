from aiogram import types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from text import *

class States(StatesGroup):
    last_name = State()
    first_name = State()
    student_id = State()
    reg_finished = State()


# Почитай про машины состояния получше и подумай, как убрать класс юзер (он точно здесь не нужен)
class User:
    def __init__(self, last_name: str='', first_name: str='', student_id: str=''):
        self.last_name = last_name
        self.first_name = first_name
        self.student_id = student_id
        self.points = 0

userdata = User()

async def reg_start(message: types.Message, state: FSMContext) -> None:
    await message.answer(WHATS_LASTNAME[int(isEnglish)])
    await state.set_state(States.first_name)


async def lastname_chosen(message: types.Message, state: FSMContext) -> None:
    await state.update_data(last_name=message.text)
    await message.answer(WHATS_FIRSTNAME[int(isEnglish)])
    await state.set_state(States.student_id)


async def first_name_chosen(message: types.Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text)
    await message.answer(WHATS_STUDENTID[int(isEnglish)])
    await state.set_state(States.reg_finished)


async def student_id_chosen(message: types.Message, state: FSMContext) -> None:
    global userdata
    await state.update_data(student_id=message.text)
    data = await state.get_data()
    userdata = User(data['last_name'], data['first_name'], data['student_id'])
    register_student(
        telegram_id=message.from_user.username,
        last_name=userdata.last_name, 
        first_name=userdata.first_name, 
        student_id=userdata.student_id)
    await message.answer(REGISTERED_SUCCESSFULLY[int(isEnglish)]+f'\n\
{userdata.last_name} {userdata.first_name} ({userdata.student_id})')
     # Вот такие длинны форматные строки нужно писать в text.py
    await state.clear()
    
