import asyncio
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from frontend.text import *     # Текст на разных языках
from frontend.register import * # Состояния в "диалогах"
from backend.database import *  # Функции бэкенда

from config import BOT_TOKEN

# Инициализация бота
dp = Dispatcher()
bot = Bot(BOT_TOKEN)

#Регистрация нужных нам функций и их хендлеров


#!!!!! !!! Вот именно поэтому и нужны роутеры, чтобы
# по отдельности не регать функции из других файлов 

dp.message.register(reg_start, States.last_name)
dp.message.register(lastname_chosen, States.first_name)
dp.message.register(first_name_chosen, States.student_id)
dp.message.register(student_id_chosen, States.reg_finished)


# start - запуск бота (регистрация)
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    userdata.student_id, userdata.last_name, userdata.first_name, userdata.points = update_userdata(message.from_user.username)
    if not userdata.last_name:
        await message.answer(LETS_SIGNUP[int(isEnglish)])
        await reg_start(message=message, state=state)
    else:
        await message.answer(LONG_TIME_NO_SEE[int(isEnglish)]+' Привет, '+userdata.first_name)
    return


# profile - личный кабинет
@dp.message(Command("profile"))
async def profile(message: types.Message) -> None:
    buttons = InlineKeyboardBuilder()
    buttons.add(
    types.InlineKeyboardButton(
        text=SIGN_UP[int(isEnglish)],
        callback_data="signing_up"), # зачем ing-овое окончание?))))))
    types.InlineKeyboardButton(
        text=EDIT_PROFILE[int(isEnglish)],
        callback_data="edit_profile")
    )
    userdata.student_id, userdata.last_name, userdata.first_name, userdata.points = update_userdata(message.from_user.username)
    await message.answer(text=f'{userdata.last_name} {userdata.first_name} ({userdata.student_id})\n\
{userdata.points} '+POINTS[int(isEnglish)], reply_markup=buttons.as_markup())


# language - смена языка на английский/русский
@dp.message(Command("language"))
async def language(message: types.Message) -> None:
    global isEnglish
    isEnglish = not isEnglish
    await message.answer(LANGUAGE_SWITCHED[int(isEnglish)])


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
