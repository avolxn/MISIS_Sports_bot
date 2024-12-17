from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from backend.cors import *
from .register import *
from .signup import days_keyboard, pairs_keyboard, gyms_keyboard
from frontend.text import *
from datetime import datetime, timedelta, time
import csv
import os

router = Router()

class ChooseSchedule(StatesGroup):
    day = State()
    pair = State()
    gym = State()
    sign_up_finished = State()


@router.callback_query(lambda callback: callback.data == "apprchoose")
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
    await callback.message.edit_text(CHOOSE_THE_DAY[0], reply_markup=await days_keyboard(language=0, prefix='appr'))
    await state.set_state(ChooseSchedule.pair)
    await callback.answer()


# Выбор пары
@router.callback_query(lambda callback: callback.data.startswith('apprweekday_'))
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

    await callback.message.edit_text(
        CHOOSE_THE_PAIR[0],
        reply_markup=await pairs_keyboard(language=0, 
                                          chosen_day=chosen_day, 
                                          prefix='appr', 
                                          first_callback="apprchoose",
                                          is_check=True)
    )
    await state.set_state(ChooseSchedule.gym)
    await callback.answer()


# Выбор зала
@router.callback_query(lambda callback: callback.data.startswith('apprpair_'))
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
    gyms = await get_coach_gyms(callback.from_user.id)
    gym_list = []
    for i in gyms:
        gym_list.append(i[0].gym)
    await callback.message.edit_text(CHOOSE_THE_GYM[0],
                                     reply_markup=await gyms_keyboard(0, 'appr', gym_list))
    await state.set_state(ChooseSchedule.sign_up_finished)
    await callback.answer()


@router.callback_query(lambda callback: (callback.data.startswith("approve") or callback.data.startswith("apprgym_")))
async def approve_students_query(callback: types.CallbackQuery, state: FSMContext) -> None:

    if callback.data.startswith("approve"):
        callback_data = callback.data.split('_')
        id = int(callback_data[1])
        student_id = int(callback_data[2])
        student = await get_userdata_by_student_id(student_id=student_id)
        await approve_signup(id=id, student_id=student_id)
        await callback.message.answer(f'{student.last_name} {student.first_name} отмечен!')
    elif callback.data.startswith("apprgym"):
        gym = callback.data.split('_')[1]
        await state.update_data(gym=int(gym))
    
    statedata = await state.get_data()
    date, pair, gym = statedata['date'], statedata['pair'], statedata['gym']
    date = date.split('.')
    date = datetime(2000+int(date[2]), int(date[1]), int(date[0]))
    signups = await get_unapproved_signups(pair=pair, gym=gym, date=date)
    buttons = InlineKeyboardBuilder()
    for signup in signups:
        student = await get_userdata_by_student_id(student_id=signup.student_id)
        buttons.row(
            types.InlineKeyboardButton(
                text=f"{student.last_name} {student.first_name} ({student.student_id})",
                callback_data=f"approve_{signup.id}_{signup.student_id}")
        )
    buttons.row(
        types.InlineKeyboardButton(text=BACK[0], callback_data='apprpair__'))
    await callback.message.edit_text(APPROVE_SIGNUPS[0],
                                     reply_markup=buttons.as_markup())
    await callback.answer()
    

@router.callback_query(lambda callback: callback.data == "getdatabase")
async def get_database_query(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Export data from the Records table to a CSV file.

    Args:
        callback (types.CallbackQuery): Callback data.
        state (FSMContext): Current state of the user in FSM.
    """
    async with async_session_maker() as session:
        # Query to join Records, Schedule, and Student tables
        query = (
            select(
                Schedule.date,
                Schedule.pair,
                Schedule.gym,
                Student.last_name,
                Student.first_name,
                Student.student_id,
                Records.approved
            )
            .select_from(Records)  # Explicitly set Records as the base table
            .join(Schedule, Records.pair_id == Schedule.id)
            .join(Student, Records.student_id == Student.student_id)
        )

        # Execute the query
        result = await session.execute(query)
        records = result.fetchall()

        # Write to CSV
        file_path = 'db.csv'
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write the header
            writer.writerow(["Дата посещения", "Пара", "Зал", "Фамилия", "Имя", "Номер студбилета", "Подтверждено"])

            # Write the data
            for record in records:
                writer.writerow([
                    record.date.strftime("%Y-%m-%d"),  # Format date
                    record.pair,
                    record.gym,
                    record.last_name,
                    record.first_name,
                    record.student_id,
                    record.approved
                ])

    # Проверка, существует ли файл
    if os.path.isfile(file_path):
        # Отправка файла пользователю
        await callback.message.answer_document(
            document=types.FSInputFile(path=file_path),
        )
    else:
        await callback.message.reply("Файл не найден. Убедитесь, что он существует.")