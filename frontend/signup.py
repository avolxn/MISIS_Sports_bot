from aiogram import types
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from .text import *
from backend.cors import *
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

router = Router()

# Машина состояний
class ChooseSchedule(StatesGroup):
    day = State()
    pair = State()
    gym = State()
    sign_up_finished = State()

def days_keyboard():
    """
    Создаем клавиатуру. Формат: "день_недели день.месяц"
    Если сегодня выходной, то выводим рабочие дни следующей недели
    Если сегодня рабочий день, то выводим рабочие дни с сегодняшнего

    !!! Пока язык русский только оставил, чуть позже изменю
    + Выводятся дни в одну строчку, когда допишем, гляну, стремно или норм
    """
    today = datetime.now()
    current_day = today.weekday()

    if current_day >= 5:
        start_next_week = today + timedelta(days=(7 - current_day))
        start_day = start_next_week.weekday()
    else:
        start_day = current_day

    buttons = []
    for i in range(start_day, start_day + 5):
        day_name = DAYS[0][i % 7]
        formatted_date = (today + timedelta(days=(i - current_day))).strftime("%d.%m")
        buttons.append([InlineKeyboardButton(text=f"{day_name} {formatted_date}",  callback_data=day_name)])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def pairs_keyboard():
    """
    Егор, сделай проверку, что выводится текущая пара и оставшиеся
    и если уже все пары закончились
    """

def gyms_keyboard():
    """
    Дима и Богдан, надо сделать проверку на то, что на пару записано <=30 человек
    Но, наверное, к первому спринту это необязательно

    Еще текст надо бы подредачить, эмодзи добавить, чтоб симпатичненько была, аля
    Зал бокса 🥊
    """

# Выбор дня недели
@router.message(ChooseSchedule.day)
async def signup_start(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    await message.answer(CHOOSE_THE_DAY[data['is_english']], reply_markup=days_keyboard())
    await state.set_state(ChooseSchedule.pair)

# Выбор зала
@router.message(ChooseSchedule.pair)
async def day_chosen(message: types.Message, state: FSMContext) -> None:
    await state.update_data(day=message.text)
    data = await state.get_data()
    await message.answer(CHOOSE_THE_PAIR[data['is_english']], reply_markup=pair_keyboard())
    await state.set_state(ChooseSchedule.gym)


# Завершение записи
@router.message(ChooseSchedule.gym)
async def pair_chosen(message: types.Message, state: FSMContext) -> None:
    await state.update_data(day=message.pair)
    data = await state.get_data()
    await message.answer(CHOOSE_THE_GYM[data['is_english']], reply_markup=gym_keyboard())
    await state.set_state(ChooseSchedule.sign_up_finished)

# Егор, заверши запись
#