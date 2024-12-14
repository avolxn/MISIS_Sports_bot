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

async def days_keyboard(is_english: int):
    """
    Создает клавиатуру с кнопками для выбора дня записи в спортзал.
    Генерирует кнопки только для рабочих дней (пн-пт):
    - Если сегодня рабочий день, показывает дни с сегодняшнего до пятницы
    - Если сегодня выходной, показывает дни со следующего понедельника до пятницы
    
    Args:
        language (int): Флаг языка интерфейса
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками вида:
            - Название дня недели на выбранном языке
            - Дата в формате DD.MM
            - callback_data в формате 'weekday_X', где X - смещение от начальной даты
    """

    # Получаем текущую дату
    today = datetime.now()
    current_day = today.weekday()

    # Если сегодня выходной (суббота или воскресенье),
    # Выводим рабочие дни с понедельника следующей недели
    if current_day >= 5:
        start_date = today + timedelta(days=(7 - current_day))
    # Если сегодня рабочий день, выводим дни с сегодняшнего дня до пятницы
    else:
        start_date = today
    start_day = start_date.weekday()
    
    # Создаем список кнопок с датами
    buttons = []
    for i in range(5-start_day):
        # Для каждого дня создаем кнопку с названием дня и датой
        current_date = start_date + timedelta(days=i)
        current_day = current_date.weekday() 
        print(i, current_date)
        # Получаем название дня на выбранном языке
        day_name = DAYS[is_english][current_day % 7]
        # Форматируем дату как DD.MM
        formatted_date = current_date.strftime("%d.%m")
        # Добавляем кнопку с названием дня и датой
        buttons.append([InlineKeyboardButton(text=f"{day_name} {formatted_date}", callback_data='weekday_'+str(i))])

    # Возвращаем клавиатуру с кнопками
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def pairs_keyboard(is_english: int):
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


async def gyms_keyboard(is_english: int):
    buttons = [[InlineKeyboardButton(text=BACK[is_english], callback_data='weekday__')]]
    for i in range(len(GYM[is_english])):
        buttons.append([InlineKeyboardButton(text=GYM[is_english][i], callback_data='gym_'+str(i))])
    return InlineKeyboardMarkup(inline_keyboard=buttons)   


@router.callback_query(lambda callback: callback.data == "sign_up")
async def signup_start(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик начала процесса записи в спортзал.
    Запускает машину состояний и показывает клавиатуру для выбора дня.
    
    Args:
        callback (types.CallbackQuery): Объект callback-запроса
        state (FSMContext): Контекст состояния пользователя
        
    Returns:
        None: Функция не возвращает значение, но отправляет сообщение с клавиатурой
        и устанавливает состояние ChooseSchedule.pair
    """
    data = await get_userdata(telegram_id=callback.from_user.id)
    is_english = int(data.is_english)
    await callback.message.answer(CHOOSE_THE_DAY[is_english], reply_markup=await days_keyboard(is_english))
    await state.set_state(ChooseSchedule.pair)
    await callback.answer()

# Выбор пары
@router.callback_query(lambda callback: callback.data.startswith('weekday_'))
async def day_chosen(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора дня недели.
    Сохраняет выбранный день в состоянии и показывает клавиатуру для выбора временной пары.

    Args:
        callback (types.CallbackQuery): Объект callback-запроса с данными о выбранном дне
        state (FSMContext): Контекст состояния пользователя
        
    Returns:
        None: Функция не возвращает значение, но обновляет сообщение с новой клавиатурой
        и устанавливает состояние ChooseSchedule.gym
    """
    day = callback.data.split('_')[1]
    if day: await state.update_data(day=int(day))
    data = await get_userdata(telegram_id=callback.from_user.id)
    is_english = int(data.is_english)
    await callback.message.edit_text(CHOOSE_THE_PAIR[is_english], reply_markup=await pairs_keyboard(is_english))
    await state.set_state(ChooseSchedule.gym)
    await callback.answer()

# Выбор зала
@router.callback_query(lambda callback: callback.data.startswith('pair_'))
async def pair_chosen(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора временной пары.
    Сохраняет выбранную пару в состоянии и показывает клавиатуру для выбора спортзала.

    Args:
        callback (types.CallbackQuery): Объект callback-запроса с данными о выбранной паре
        state (FSMContext): Контекст состояния пользователя
        
    Returns:
        None: Функция не возвращает значение, но обновляет сообщение с новой клавиатурой
        и устанавливает состояние ChooseSchedule.sign_up_finished
    """
    pair = callback.data.split('_')[1]
    await state.update_data(pair=int(pair))
    data = await get_userdata(telegram_id=callback.from_user.id)
    is_english = int(data.is_english)
    await callback.message.edit_text(CHOOSE_THE_GYM[is_english], reply_markup=await gyms_keyboard(is_english))
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
    data = await get_userdata(telegram_id=callback.from_user.id)
    await sign_up_to_section(telegram_id=callback.from_user.id, student_id=data.student_id)
    is_english = int(data.is_english)
    message = (
        f"{SIGNED_UP_SUCCESSFULLY[is_english]}\n"
        f"{CHOSEN_DAY[is_english]}: {DAYS[is_english][day % 7]}\n"
        f"{CHOSEN_PAIR[is_english]}: {pair}\n"
        f"{CHOSEN_GYM[is_english]}: {GYM[is_english][gym]}\n"
    )

    await callback.message.delete()
    await callback.message.answer(message)
    await state.clear()
    await callback.answer()