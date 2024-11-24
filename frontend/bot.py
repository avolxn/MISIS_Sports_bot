import asyncio
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .text import *     # Текст на разных языках
from .register import * # Состояния в "диалогах"
from .register import router as register_router
from backend.database import *  # Функции бэкенда

from config import BOT_TOKEN

# Инициализация бота
dp = Dispatcher()
bot = Bot(BOT_TOKEN)

# Подключаем все сообщения регистрации
dp.include_router(register_router)


# start - запуск бота (регистрация)
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    buffer = await get_userdata(message.from_user.username)
    await state.update_data(is_english=False)
    userdata = await state.get_data()
    if not buffer:
        await message.answer(LETS_SIGNUP[userdata['is_english']])
        await reg_start(message=message, state=state)
    else:
        await state.set_data({
            'student_id': buffer.student_id,
            'last_name': buffer.last_name,
            'first_name': buffer.first_name,
            'is_english': False,
            'points': buffer.points,
        })
        userdata = await state.get_data()
        await message.answer(LONG_TIME_NO_SEE[int(userdata['is_english'])]+' Привет, '+userdata['first_name'])
    return


# profile - личный кабинет
@dp.message(Command("profile"))
async def profile(message: types.Message, state: FSMContext) -> None:
    userdata = await state.get_data()
    buttons = InlineKeyboardBuilder()
    buttons.add(
    types.InlineKeyboardButton(
        text=SIGN_UP[int(userdata['is_english'])],
        callback_data="sign_up"), # зачем ing-овое окончание?)))))) 
        # Ну потому что.... эээ... Ну потому что... ну потому что потому!
    types.InlineKeyboardButton(
        text=EDIT_PROFILE[int(userdata['is_english'])],
        callback_data="edit_profile")
    )
    await message.answer(text=f'{userdata['last_name']} {userdata['first_name']} ({userdata['student_id']})\n\
{userdata['points']} '+POINTS[int(userdata['is_english'])], reply_markup=buttons.as_markup())


# language - смена языка на английский/русский
@dp.message(Command("language"))
async def language(message: types.Message, state: FSMContext) -> None:
    userdata = await state.get_data()
    await state.update_data(is_english=not(userdata['is_english']))
    await message.answer(LANGUAGE_SWITCHED[not(userdata['is_english'])])


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
