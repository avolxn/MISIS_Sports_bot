from aiogram import types
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from .text import *
from backend.cors import *

router = Router()

# Машина состояний
class ChooseSchedule(StatesGroup):
    day = State()
    pair = State()
    gym = State()

@router.message(ChooseSchedule.day)
async def signup_start(message: types.Message, state: FSMContext) -> None:
    pass

# Получение фамилии
@router.message(ChooseSchedule.pair)
async def day_chosen(message: types.Message, state: FSMContext) -> None:
    pass

# Получение имени
@router.message(ChooseSchedule.gym)
async def pair_chosen(message: types.Message, state: FSMContext) -> None:
    pass