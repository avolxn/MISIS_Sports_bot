from aiogram import types, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from .text import *
from backend.cors import *
import re
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.filters import Command
from config import SUPERUSER_ID
import random
import string

router = Router()


# Машина состояний тренера
class Coach(StatesGroup):
    first_name = State()
    last_name = State()
    patronymic = State()
    gyms = State()


async def gyms_coaches_keyboard(picked_gyms) -> InlineKeyboardMarkup:
    """
    Получаем клавиатуру с залами
    """
    buttons = list()
    for i in range(len(GYMS_ALLOWED)):
        if picked_gyms[i]:
            text = ("✅ ") + GYMS_ALLOWED[i]
        else:
            text = ("❌ ") + GYMS_ALLOWED[i]
        buttons.append(
            [InlineKeyboardButton(text=text, callback_data="pickme_gym_" + str(i))]
        )
    buttons.append(
        [InlineKeyboardButton(text=FINISH_GYMS, callback_data="finish_gyms")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("reg_coach"))
async def reg_coach_command(message: Message, state: FSMContext):
    """
    Регистрация тренера
    """
    if message.from_user.id == int(SUPERUSER_ID):
        await message.answer(FIRST_NAME_COACH)
        await state.set_state(Coach.first_name)


@router.message(Coach.first_name)
async def first_name_coach(message: types.Message, state: FSMContext) -> None:
    """
    Регистрация имени тренера
    """
    if not re.match(r"^[А-Яа-яЁё]+(?:[- ]?[А-Яа-яЁё]+)*$", message.text):
        await message.answer(ERROR_FIRST_NAME_COACH)
    else:
        await message.answer(LAST_NAME_COACH)
        await state.update_data(first_name=message.text)
        await state.set_state(Coach.last_name)


@router.message(Coach.last_name)
async def last_name_coach(message: types.Message, state: FSMContext) -> None:
    """
    Регистрация фамилии тренера
    """
    if not re.match(r"^[А-Яа-яЁё]+(?:[- ]?[А-Яа-яЁё]+)*$", message.text):
        await message.answer(ERROR_LAST_NAME_COACH)
    else:
        kb = [[types.KeyboardButton(text=NO_PATRONYMIC)]]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

        await message.answer(PATRONYMIC_COACH, reply_markup=keyboard)
        await state.update_data(last_name=message.text)
        await state.set_state(Coach.patronymic)


@router.message(Coach.patronymic)
async def patronymic_coach(message: types.Message, state: FSMContext) -> None:
    """
    Регистрация отчества тренера
    """
    if (not re.match(r"^[А-Яа-яЁё]+(?:[- ]?[А-Яа-яЁё]+)*$", message.text)) and (
        message.text != NO_PATRONYMIC
    ):
        kb = [[types.KeyboardButton(text=NO_PATRONYMIC)]]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
        await message.answer(ERROR_PATRONYMIC_COACH, reply_markup=keyboard)
    else:
        await state.update_data(
            patronymic_coach=(None if message.text == NO_PATRONYMIC else message.text)
        )
        gyms = [False for i in range(len(GYMS_ALLOWED))]
        kb = await gyms_coaches_keyboard(gyms)
        await message.answer(
            GYMS_QUESTION, reply_markup=ReplyKeyboardRemove(remove_keyboard=True)
        )
        await message.answer(GYMS_LIST, reply_markup=kb)
        await state.set_state(Coach.gyms)
        await state.update_data(gyms=gyms)


@router.callback_query(
    lambda callback: callback.data.startswith("pickme_gym_"), Coach.gyms
)
async def gyms_for_coach(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Регистрация залов тренера
    """
    picked_gym = int(callback.data.split("_")[2])
    gyms = (await state.get_data())["gyms"]
    gyms[picked_gym] = not gyms[picked_gym]
    kb = await gyms_coaches_keyboard(gyms)
    await callback.message.edit_reply_markup(callback.inline_message_id, kb)


@router.callback_query(lambda callback: callback.data == "finish_gyms", Coach.gyms)
async def finish_coach_registration(
    callback: types.CallbackQuery, state: FSMContext
) -> None:
    """
    Завершение регистрации тренера
    """
    data = await state.get_data()
    first_name = data["first_name"]
    last_name = data["last_name"]
    patronymic = data["patronymic_coach"]
    gyms = data["gyms"]
    secret_token = "".join(
        random.choices(string.ascii_letters, k=50)
    )  # Генерация секретного токена
    coach_id = await register_coach(first_name, last_name, patronymic, secret_token)
    await register_coaches_to_gyms(coach_id, gyms)
    await callback.message.answer(COACH_REG_FINISH % (secret_token))
    await callback.message.delete()
