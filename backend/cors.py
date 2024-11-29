from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import insert, select, and_, update, delete
from backend.models import Student, Schedule
from backend.database import async_session_maker
from datetime import timedelta, datetime
import sqlalchemy as db


async def register_student(telegram_id: str, student_id: str, last_name: str, first_name: str) -> None:
    async with async_session_maker() as session:
        new_student = Student(
            telegram_id=telegram_id, 
            student_id=int(student_id),
            last_name=last_name, 
            first_name=first_name,
            points=0
        )
        session.add(new_student)
        await session.commit()


async def get_userdata(telegram_id: str):
    async with async_session_maker() as session:
        query_select = db.select(Student).where(Student.telegram_id == telegram_id)
        result = await session.execute(query_select)
        user_data = result.scalars().first()  # Извлечение первой записи (или None, если записи нет)
        if user_data is None:
            return False
        return user_data


async def get_pair_info(id: int):
    pass


async def unsign(id: int) -> None: # Пока не работает и не используется!
    async with async_session_maker() as session:
        query_update = (
            update(Schedule)
            .where(Schedule.id == id)
            .values(free_slots_left=Schedule.free_slots_left + 1)
        )
        await session.execute(query_update)
        await session.commit()


async def sign_up_to_section(id: int, telegram_id: str) -> None:
    async with async_session_maker() as session:
        async with session.begin():
            query_update_schedule = (
                update(Schedule)
                .where(Schedule.id == id)
                .values(free_slots_left=Schedule.free_slots_left - 1)
            )
            query_update_student = (
                update(Student)
                .where(Student.telegram_id == telegram_id)
                .values(points=Student.points + 10)
            )
            await session.execute(query_update_schedule)
            await session.execute(query_update_student)
        #ПРОВЕРКУ ПОСЕЩАЕМОСТИ РЕАЛИЗУЕМ ПОТОМ!!!