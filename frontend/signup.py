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


async def days_keyboard(language: int, prefix: str = '') -> InlineKeyboardMarkup:
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

    today = datetime.now()
    current_day = today.weekday()

    if current_day >= 5:
        start_date = today + timedelta(days=(7 - current_day))
    else:
        start_date = today

    start_day = start_date.weekday()
    buttons = list()
    for i in range(5-start_day):
        current_date = start_date + timedelta(days=i) 
        current_day = current_date.weekday()  
        # Получаем название дня на выбранном языке 
        day_name = DAYS[language][current_day % 7] 
        # Форматируем дату как DD.MM 
        formatted_date = current_date.strftime("%d.%m") 
        # Добавляем кнопку с названием дня и датой 
        buttons.append([InlineKeyboardButton(text=f"{day_name} {formatted_date}", callback_data=prefix+'weekday_'+str(i)+'_'+current_date.strftime("%d.%m.%y"))]) 

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def pairs_keyboard(language: int, chosen_day: int, prefix: str = '', first_callback: str = "sign_up", is_check: bool = False) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с доступными временными парами.
    Показывает только те пары, которые:
    - Еще не начались (для текущего дня)
    - Все пары (для будущих дней)

    Args:
        language (int): Флаг языка интерфейса
        chosen_day (int): Смещение выбранного дня от текущей даты

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками доступных пар
    """
    pairs_schedule = [
        {"pair": 1, "start": time(9, 0), "end": time(10, 35)},
        {"pair": 2, "start": time(10, 50), "end": time(12, 25)},
        {"pair": 3, "start": time(12, 40), "end": time(14, 15)},
        {"pair": 4, "start": time(14, 30), "end": time(16, 5)},
    ]

    # Получаем текущую дату и время
    now = datetime.now()
    current_time = now.time()

    # Определяем дату выбранного дня
    if now.weekday() >= 5:  # если сегодня выходной
        start_date = now + timedelta(days=(7 - now.weekday()))  # следующий понедельник
    else:
        start_date = now
    chosen_date = start_date + timedelta(days=chosen_day)

    buttons = list()

    # Для текущего дня проверяем время
    # Для будущих дней показываем все пары
    for pair in pairs_schedule:
        if (chosen_date.date() != now.date()) or (current_time < pair["start"]) or is_check:
            start = pair['start']
            end = pair['end']
            buttons.append([InlineKeyboardButton(
                text=f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}",
                callback_data=f'{prefix}pair_{pair["pair"]}'
            )])

    buttons.append([InlineKeyboardButton(text=BACK[language], callback_data='sign_up')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def gyms_keyboard(language: int, prefix: str = '') -> InlineKeyboardMarkup:
    buttons = list()
    for i in range(len(GYM[language])):
        buttons.append([InlineKeyboardButton(text=GYM[language][i], callback_data=f'{prefix}gym_' + str(i+1))])
    buttons.append([InlineKeyboardButton(text=BACK[language], callback_data=f'{prefix}weekday__')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def cancel_keyboard(language: int, record_id: int, prefix: str = '') -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=CANCEL_SIGNUP[language], callback_data=f'{prefix}cancel_{str(record_id)}')]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def back_keyboard(language: int) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=BACK[language], callback_data=f'pair__')]]
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
    await callback.message.edit_text(CHOOSE_THE_DAY[data.language],
                                     reply_markup=await days_keyboard(language=data.language))
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
    chosen_day = 0

    if day:
        chosen_day = int(day)
        await state.update_data(day=chosen_day, date=callback.data.split('_')[2])
    else:
        statedata = await state.get_data()
        chosen_day = statedata['day']
    
    data = await get_userdata(telegram_id=callback.from_user.id)
    await callback.message.edit_text(
        CHOOSE_THE_PAIR[data.language],
        reply_markup=await pairs_keyboard(language=data.language, chosen_day=chosen_day)
    )
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
    if pair:
        await state.update_data(pair=int(pair))
    data = await get_userdata(telegram_id=callback.from_user.id)
    await callback.message.edit_text(CHOOSE_THE_GYM[data.language],
                                     reply_markup=await gyms_keyboard(language=data.language))
    await state.set_state(ChooseSchedule.sign_up_finished)
    await callback.answer()


# Завершение записи
@router.callback_query(lambda callback: callback.data.startswith('gym_'))
async def gym_chosen(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора спортзала.
    Сохраняет выбранный зал в состоянии и показывает сообщение об успешной записи.

    Args:
        callback (types.CallbackQuery): Объект callback-запроса с данными о выбранном зале
        state (FSMContext): Контекст состояния пользователя

    Returns:
        None: Функция не возвращает значение, но обновляет сообщение с новой клавиатурой
        и очищает состояние.
    """
    gym = callback.data.split('_')[1]
    await state.update_data(gym=int(gym))
    statedata = await state.get_data()
    date, day, pair, gym = statedata['date'], statedata['day'], statedata['pair'], statedata['gym']
    data = await get_userdata(telegram_id=callback.from_user.id)
    
    date = date.split('.')
    date = datetime(2000+int(date[2]), int(date[1]), int(date[0]))
    
    record_id = await sign_up_to_section(
        telegram_id=callback.from_user.id, 
        student_id=data.student_id, 
        pair=pair,
        gym=gym,
        date=date
    )
    if record_id:
        message = (
            f"{SIGNED_UP_SUCCESSFULLY[data.language]}\n"
            f"{CHOSEN_DAY[data.language]}: {DAYS[data.language][(day % 7) + 1]} {date.strftime("%d.%m")}\n"
            f"{CHOSEN_PAIR[data.language]}: {pair}\n"
            f"{CHOSEN_GYM[data.language]}: {GYM[data.language][gym-1]}\n\n"
            f"{IF_YOU_WONT_COME[data.language]}\n"
        )
        await callback.message.edit_text(message,
                                        reply_markup=await cancel_keyboard(language=data.language, record_id=record_id))
        await state.clear()
    else:
        await callback.message.edit_text(ALREADY_SIGNED_UP[data.language], reply_markup=await back_keyboard(language=data.language))
    await callback.answer()


@router.callback_query(lambda callback: callback.data.startswith('cancel_'))
async def signup_cancelled(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Отмена записи на пару.
    Сохраняет выбранный зал в состоянии и показывает сообщение об успешной записи.

    Args:
        callback (types.CallbackQuery): Объект callback-запроса с данными об идентификаторе записи
        state (FSMContext): Контекст состояния пользователя

    Returns:
        None: Функция не возвращает значение, но удаляет сообщение и создаёт новое.
    """
    record_id = int(callback.data.split('_')[1])
    await unsign(record_id=record_id)
    data = await get_userdata(telegram_id=callback.from_user.id)
    message = CANCELLED[data.language]
    await callback.message.delete()
    await callback.message.answer(message)
    await state.clear()
    await callback.answer()


