import asyncio
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .text import *     # Текст на разных языках
from .register import * # Состояния в "диалогах"
from .register import router as register_router
from .signup import router as signup_router
from .edit_profile import router as edit_profile_router
from backend.database import *  # Функции бэкенда

from config import BOT_TOKEN

# Инициализация бота
dp = Dispatcher()
bot = Bot(BOT_TOKEN)

# Подключаем все сообщения регистрации
dp.include_router(edit_profile_router)
dp.include_router(register_router)
dp.include_router(signup_router)


# start - запуск бота (регистрация)
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    """
    Если пользователь новый, то перенаправление на регистрацию.
    Если пользователь уже есть в БД, то бот пришлёт приветствие.
    Args:
        message (types.Message): Отправленное сообщение
        state (FSMContext): Машина состояний
    Returns: None
    """
    await state.clear()
    data = await get_userdata(message.from_user.id)
    if not data:
        #await message.answer(LETS_SIGNUP[language])
        await reg_start(message=message, state=state)
    else:
        await message.answer(LONG_TIME_NO_SEE[int(data.language)]%(data.first_name))
    return


# profile - личный кабинет
@dp.message(Command("profile"))
async def profile(message: types.Message, state: FSMContext) -> None:
    """
    Сообщение с выводом ФИО и баллов студента. Отсюда можно записаться на пару.
    Если пользователь не зарегистрирован, то его переносит на регистрацию.
    Args: 
        message (types.Message): Отправленное сообщение
        state (FSMContext): Машина состояний
    Retur(ns: None
    """
    await state.clear()
    
    data = await get_userdata(message.from_user.id)
    if not data:
        await reg_start(message=message, state=state)
        return
    language = int(data.language)
    buttons = InlineKeyboardBuilder()
    buttons.row(
    types.InlineKeyboardButton(
        text=SIGN_UP[language],
        callback_data="sign_up")
    )
    buttons.row(
    types.InlineKeyboardButton(
        text=EDIT_PROFILE[language],
        callback_data="edit_profile")
    )
    await message.answer(text=PROFILE_TEXT[language]%(data.last_name, data.first_name, data.student_id, data.points), 
                         reply_markup=buttons.as_markup())

async def main() -> None:
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
