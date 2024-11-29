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
    buffer = await get_userdata(message.from_user.username)
    await state.update_data(is_english=False)
    data = await state.get_data()
    is_english = int(data.get('is_english', False))
    if not buffer:
        await message.answer(LETS_SIGNUP[is_english])
        await reg_start(message=message, state=state)
    else:
        await state.set_data({
            'student_id': buffer.student_id,
            'last_name': buffer.last_name,
            'first_name': buffer.first_name,
            'is_english': False,
            'points': buffer.points,
        })
        data = await state.get_data()
        first_name = data.get('first_name')
        await message.answer(LONG_TIME_NO_SEE[is_english]%(first_name))
    return


# profile - личный кабинет
@dp.message(Command("profile"))
async def profile(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    last_name = data.get('last_name')
    first_name = data.get('first_name')
    student_id = data.get('student_id')
    points = data.get('points')
    is_english = int(data.get('is_english', False))
    buttons = InlineKeyboardBuilder()
    buttons.add(
    types.InlineKeyboardButton(
        text=SIGN_UP[is_english],
        callback_data="sign_up"),
    types.InlineKeyboardButton(
        text=EDIT_PROFILE[is_english],
        callback_data="edit_profile")
    )
    await message.answer(text=PROFILE_TEXT[is_english]%(last_name, first_name, student_id, str(points)), 
                         reply_markup=buttons.as_markup())


# language - смена языка на английский/русский
@dp.message(Command("language"))
async def language(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    is_english = int(data.get('is_english', False))
    await state.update_data(is_english=not(is_english))
    await message.answer(LANGUAGE_SWITCHED[not(is_english)])


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
