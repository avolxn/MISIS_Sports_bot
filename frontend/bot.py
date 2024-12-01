import asyncio
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .text import *     # Текст на разных языках
from .register import * # Состояния в "диалогах"
from .register import router as register_router
from .signup import router as signup_router
from backend.database import *  # Функции бэкенда

from config import BOT_TOKEN

# Инициализация бота
dp = Dispatcher()
bot = Bot(BOT_TOKEN)

# Подключаем все сообщения регистрации
dp.include_router(register_router)
dp.include_router(signup_router)


# start - запуск бота (регистрация)
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    data = await get_userdata(message.from_user.id)
    if not data:
        #await message.answer(LETS_SIGNUP[is_english])
        await reg_start(message=message, state=state)
    else:
        await message.answer(LONG_TIME_NO_SEE[int(data.is_english)]%(data.first_name))
    return


# profile - личный кабинет
@dp.message(Command("profile"))
async def profile(message: types.Message, state: FSMContext) -> None:
    data = await get_userdata(message.from_user.id)
    if not data:
        await reg_start(message=message, state=state)
        return
    is_english = int(data.is_english)
    buttons = InlineKeyboardBuilder()
    buttons.row(
    types.InlineKeyboardButton(
        text=SIGN_UP[is_english],
        callback_data="sign_up")
    )
    buttons.row(
    types.InlineKeyboardButton(
        text=EDIT_PROFILE[is_english],
        callback_data="edit_profile")
    )
    await message.answer(text=PROFILE_TEXT[is_english]%(data.last_name, data.first_name, data.student_id, data.points), 
                         reply_markup=buttons.as_markup())


# language - смена языка на английский/русский
@dp.message(Command("language"))
async def language(message: types.Message, state: FSMContext) -> None:
    await update_language(message.from_user.id)
    data = await get_userdata(message.from_user.id)
    is_english = int(data.is_english)
    await message.answer(LANGUAGE_SWITCHED[is_english])


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
