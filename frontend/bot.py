import asyncio
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, types
import os
from dotenv import load_dotenv

#Загрузка ключей с .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

#Инициализация бота
dp = Dispatcher()
bot = Bot(BOT_TOKEN)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Давай сначала зарегистрируемся.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())