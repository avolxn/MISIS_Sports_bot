from aiogram import types
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from .text import *
from backend.cors import *
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta, time

router = Router()

# Машина состояний
class ChooseSchedule(StatesGroup):
    day = State()
    pair = State()
    gym = State()
    sign_up_finished = State()

def days_keyboard():
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
        buttons.append([InlineKeyboardButton(text=f"{day_name} {formatted_date}", callback_data='weekday_'+day_name)])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def pairs_keyboard():
    pairs_schedule = [
            {"pair": 1, "start": time(9, 0), "end": time(10, 35)},
            {"pair": 2, "start": time(10, 50), "end": time(12, 25)},
            {"pair": 3, "start": time(12, 40), "end": time(14, 15)},
            {"pair": 4, "start": time(14, 30), "end": time(16, 5)},
        ]
    current_time = time(0,0) # datetime.now().time()
    buttons = []
    for pair in pairs_schedule:
        if current_time < pair["start"]: 
            start = pair['start']
            end = pair['start']
            buttons.append([InlineKeyboardButton(text="%i: %02d:%02d - %02d:%02d"%(pair['pair'], start.hour, start.minute, end.hour, end.minute), 
                                                 callback_data='pair_'+str(pair['pair']))])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def gyms_keyboard():
    """
    Дима и Богдан, надо сделать проверку на то, что на пару записано <= 30 человек
    Но, наверное, к первому спринту это необязательно

    Еще текст надо бы подредачить, эмодзи добавить, чтоб симпатичненько была, аля
    Зал бокса 🥊
    """
    buttons = list()
    for i in range(len(GYM[0])):
        buttons.append([InlineKeyboardButton(text=GYM[0][i], callback_data='gym_'+str(i+1))])
    return InlineKeyboardMarkup(inline_keyboard=buttons)   


@router.callback_query(lambda callback: callback.data == "sign_up")
async def signup_start(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    is_english = int(data.get('is_english', False))
    await callback.message.answer(CHOOSE_THE_DAY[is_english], reply_markup=days_keyboard())
    await state.set_state(ChooseSchedule.pair)
    await callback.answer()

# Выбор зала
@router.callback_query(lambda callback: callback.data.startswith('weekday_'))
async def day_chosen(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.update_data(day=callback.data.split('_')[1])
    data = await state.get_data()
    is_english = int(data.get('is_english', False))
    await callback.message.answer(CHOOSE_THE_PAIR[is_english], reply_markup=pairs_keyboard())
    await state.set_state(ChooseSchedule.gym)
    await callback.answer()

# Завершение записи
@router.callback_query(lambda callback: callback.data.startswith('pair_'))
async def pair_chosen(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.update_data(day=callback.data.split('_')[1])
    data = await state.get_data()
    is_english = int(data.get('is_english', False))
    await callback.message.answer(CHOOSE_THE_GYM[is_english], reply_markup=gyms_keyboard())
    await state.set_state(ChooseSchedule.sign_up_finished)
    await callback.answer()

# Егор, заверши запись
#