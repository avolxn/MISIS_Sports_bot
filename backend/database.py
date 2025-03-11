from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession 
from sqlalchemy.orm import sessionmaker 
from .models import * 
import sqlalchemy as db 
from config import DATABASE_URL, SUPERUSER_ID, SUPERUSER_FIRST_NAME, SUPERUSER_LAST_NAME, SUPERUSER_PATRONYMIC # DATABASE_URL - это ссылка на подключение к бд. в ней 

# Подключаем базу данных
engine = create_async_engine(DATABASE_URL, echo=True, future=True) 
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) 


async def get_coach(telegram_id: int): 
    """
    Получаем данные супер админа
    """
    async with async_session_maker() as session: 
        query_select = db.select(Coach).where(Coach.telegram_id == int(telegram_id)) 
        result = await session.execute(query_select) 
        coach_data = result.scalars().first() 
        if coach_data is None: 
            return False 
        return coach_data 
 

async def register_coach(telegram_id: str, first_name: str, last_name: str, patronymic: str, is_admin: bool, secret_token: str=None) -> None: 
    """
    Добавляем супер админа
    """
    if not (await get_coach(telegram_id)): 
        async with async_session_maker() as session: 
            new_coach = Coach( 
                telegram_id=int(telegram_id),  
                first_name=first_name, 
                last_name=last_name,  
                patronymic=patronymic,  
                is_approved=True, 
                secret_token=secret_token 
            ) 
            session.add(new_coach) 
            await session.commit() 
 
async def init_db(): 
    """
    Запускаем генерацию таблиц и при надобности заносим супер админа
    """
    async with engine.begin() as conn: 
        await conn.run_sync(Base.metadata.create_all) 
    
    if (not await get_coach(SUPERUSER_ID)): 
        await register_coach(SUPERUSER_ID, SUPERUSER_FIRST_NAME, SUPERUSER_LAST_NAME, SUPERUSER_PATRONYMIC, True)