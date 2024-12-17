import os
from dotenv import load_dotenv

# Конфиг нужен для подгрузки .env в переменные, которые уже напрямую импортируются в бота и бд

# Load the environment variables from the .env file
load_dotenv()

# Access the variables
DATABASE_URL = os.getenv('DATABASE_URL') 
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_RESERVE_TOKEN = os.getenv('BOT_RESERVE_TOKEN')
SUPERUSER_ID = os.getenv('SUPERUSER_ID')
SUPERUSER_FIRST_NAME = os.getenv('SUPERUSER_FIRST_NAME')
SUPERUSER_LAST_NAME = os.getenv('SUPERUSER_LAST_NAME')
SUPERUSER_PATRONYMIC = os.getenv('SUPERUSER_PATRONYMIC')