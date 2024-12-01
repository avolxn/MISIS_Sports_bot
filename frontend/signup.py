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

def days_keyboard(is_english: int):
    today = datetime.now()
    current_day = today.weekday()

    if current_day >= 5:
        start_date = today + timedelta(days=(7 - current_day))
    else:
        start_date = today

    buttons = []
    for i in range(start_date.weekday(), 5):
        current_date = start_date + timedelta(days=i)
        day_name = DAYS[is_english][i % 7]
        formatted_date = current_date.strftime("%d.%m")
        buttons.append([InlineKeyboardButton(text=f"{day_name} {formatted_date}", callback_data='weekday_'+str(i))])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def pairs_keyboard(is_english: int):
    pairs_schedule = [
            {"pair": 1, "start": time(9, 0), "end": time(10, 35)},
            {"pair": 2, "start": time(10, 50), "end": time(12, 25)},
            {"pair": 3, "start": time(12, 40), "end": time(14, 15)},
            {"pair": 4, "start": time(14, 30), "end": time(16, 5)},
        ]
    current_time = time(0,0) # datetime.now().time()
    buttons = [[InlineKeyboardButton(text=BACK[is_english], callback_data='sign_up')]]
    for pair in pairs_schedule:
        if current_time < pair["start"]:
            start = pair['start']
            end = pair['end']
            buttons.append([InlineKeyboardButton(text="%02d:%02d - %02d:%02d"%(start.hour, start.minute, end.hour, end.minute),
                                                 callback_data='pair_'+str(pair['pair']))])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def gyms_keyboard(is_english: int):
    """
    Дима и Богдан, надо сделать проверку на то, что на пару записано <= 30 человек
    Но, наверное, к первому спринту это необязательно.
    """
    buttons = [[InlineKeyboardButton(text=BACK[is_english], callback_data='weekday__')]]
    for i in range(len(GYM[is_english])):
        buttons.append([InlineKeyboardButton(text=GYM[is_english][i], callback_data='gym_'+str(i))])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(lambda callback: callback.data == "sign_up")
async def signup_start(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await get_userdata(telegram_id=callback.from_user.id)
    is_english = int(data.is_english)
    await callback.message.answer(CHOOSE_THE_DAY[is_english], reply_markup=days_keyboard(is_english))
    await state.set_state(ChooseSchedule.pair)
    await callback.answer()

# Выбор пары
@router.callback_query(lambda callback: callback.data.startswith('weekday_'))
async def day_chosen(callback: types.CallbackQuery, state: FSMContext) -> None:
    day = callback.data.split('_')[1]
    if day: await state.update_data(day=int(day))
    data = await get_userdata(telegram_id=callback.from_user.id)
    is_english = int(data.is_english)
    await callback.message.edit_text(CHOOSE_THE_PAIR[is_english], reply_markup=pairs_keyboard(is_english))
    await state.set_state(ChooseSchedule.gym)
    await callback.answer()

# Егор, заверши запись
# Выбор зала
@router.callback_query(lambda callback: callback.data.startswith('pair_'))
async def pair_chosen(callback: types.CallbackQuery, state: FSMContext) -> None:
    pair = callback.data.split('_')[1]
    await state.update_data(pair=int(pair))
    data = await get_userdata(telegram_id=callback.from_user.id)
    is_english = int(data.is_english)
    await callback.message.edit_text(CHOOSE_THE_GYM[is_english], reply_markup=gyms_keyboard(is_english))
    await state.set_state(ChooseSchedule.sign_up_finished)
    await callback.answer()

#Завершение записи
@router.callback_query(lambda callback: callback.data.startswith('gym_'))
async def gym_chosen(callback: types.CallbackQuery, state: FSMContext) -> None:
    gym = callback.data.split('_')[1]
    await state.update_data(gym=int(gym))
    statedata = await state.get_data()
    day = statedata['day']
    pair = statedata['pair']
    gym = statedata['gym']
    print(day, pair, gym)
    data = await get_userdata(telegram_id=callback.from_user.id)
    is_english = int(data.is_english)

    message = (
        f"{SIGNED_UP_SUCCESSFULLY[is_english]} \n"
        f"{CHOOSEN_DAY[is_english]}: {DAYS[is_english][day % 7]}, \n"
        f"{CHOOSEN_PAIR[is_english]}: {pair}, \n"
        f"{CHOOSEN_GYM[is_english]}: {GYM[is_english][gym]}. \n"
    )

    await callback.message.edit_text(message)


    await state.clear()
    await callback.answer()