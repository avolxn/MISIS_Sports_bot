from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models import *


from config import DATABASE_URL # DATABASE_URL - это ссылка на подключение к бд. в ней
# есть и пароль и адрес и всё остальное. Пока что сам создай postgresql БД у себя на компе
# и с ней работай. Я же (Богдан), потом создам общую БД и скину вам ссылку

# Это файл, через который идёт подключение к БД

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)