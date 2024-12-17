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
from .admin_features import router as admin_router
from .coaches import * 
from .coaches import router as coaches_router
from backend.database import *  # Функции бэкенда

from config import BOT_TOKEN, BOT_RESERVE_TOKEN

# Инициализация бота
dp = Dispatcher()
bot = Bot(BOT_TOKEN)

# Подключаем все сообщения регистрации
dp.include_router(edit_profile_router)
dp.include_router(register_router)
dp.include_router(signup_router)
dp.include_router(admin_router)
dp.include_router(coaches_router)


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
    if len(message.text) != 6: 
        try: 
            secret_token = message.text.split()[1] 
            if len(secret_token) == 50: 
                res = await get_coach_by_secret(secret_token) 
                if res: 
                    if not res.is_approved: 
                        await verify_secret(res.id, message.from_user.id) 
                        await message.answer(VERIFY_SECRET) 
                    else: 
                        await message.answer(VERIFIED_ALREADY) 
                     
        except Exception: 
            pass 
    else: 
        if message.from_user.id != int(SUPERUSER_ID) : 
            await state.clear() 
            data = await get_userdata(message.from_user.id) 
            if not data: 
                coach = await get_coach(message.from_user.id) 
                if not coach: 
                    await reg_start(message=message, state=state) 
                else: 
                    await message.answer(VERIFIED_ALREADY) 
            else: 
                await message.answer(LONG_TIME_NO_SEE[int(data.language)]%(data.first_name)) 
        else: 
            await message.answer(VERY_FIRST_COACH_REG)


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
    user_data = await get_userdata(message.from_user.id)
    if not user_data: 
        coach = await get_coach(message.from_user.id) 
        if not coach: 
            await reg_start(message=message, state=state)
        else:
            # Меню для тренера
            buttons = InlineKeyboardBuilder()
            buttons.row(
            types.InlineKeyboardButton(
                text=APPROVE_SIGNUPS[0],
                callback_data="apprchoose")
            )
            buttons.row(
            types.InlineKeyboardButton(
                text=EXPORT_DB,
                callback_data="getdatabase"
            )
        )
            await message.answer(text=COACH_MENU%(coach.last_name, coach.first_name, (coach.patronymic if coach.patronymic else '')), 
                                 reply_markup=buttons.as_markup())
    else:
        # Меню для студента
        language = int(user_data.language)
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
        await message.answer(text=PROFILE_TEXT[language]%(user_data.last_name, user_data.first_name, user_data.student_id, user_data.points), 
                         reply_markup=buttons.as_markup())

async def main() -> None:
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
