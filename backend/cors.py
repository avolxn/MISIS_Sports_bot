from aiogram.types import Message
from sqlalchemy import insert, select, and_, update, delete
from backend.models import User
from backend.database import async_session_maker
from datetime import timedelta, datetime


#  Эти функции - это просто пример того, как их надо реализовывать.
# В самих же файлах бота ты просто делаешь import * from backend.cors и взаимодействуешь с ними

async def create_user(message: Message):
    async with async_session_maker() as session:
        query = select(User.id).where(User.id == message.from_user.id)
        res = (await session.execute(query)).fetchone()
        if not res:
            user_object = User(
                id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
            )
            session.add(user_object)
            await session.commit()


async def get_user_subscription(user_id):
    async with async_session_maker() as session:
        query = select(User.expiration).where(User.id == user_id)
        res = (await session.execute(query)).fetchone()
        return res[0]


async def update_trial_subscription(user_id):
    async with async_session_maker() as session:
        three_days = datetime.now() + timedelta(days=3)
        stmt = update(User).where(User.id == user_id).values({"expiration": three_days, "subscribed": True})
        await session.execute(stmt)
        await session.commit()


async def update_subscription(user_id, month):
    async with async_session_maker() as session:
        query = select(User.expiration).where(User.id == user_id)
        res = (await session.execute(query)).fetchone()
        if res[0] < datetime.now():
            month = datetime.now() + timedelta(days=month * 30)
        else:
            month = res[0] + timedelta(days=month * 30)
        stmt = update(User).where(User.id == user_id).values({"expiration": month, "subscribed": True})
        await session.execute(stmt)
        await session.commit()


async def get_users_to_revoke():
    async with async_session_maker() as session:
        query = select(User).where(User.subscribed==True)
        res = (await session.execute(query)).fetchall()
        users = []
        for u in res:
            if u[0].expiration <= datetime.now():
                users.append(u[0])
        return users
    
async def revoke_user_subscription(user_id):
    async with async_session_maker() as session:
        stmt = update(User).where(User.id == user_id).values({"subscribed": False})
        await session.execute(stmt)
        await session.commit()