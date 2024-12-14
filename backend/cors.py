from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import insert, select, and_, update, delete
from backend.models import Student, Schedule, Records
from backend.database import async_session_maker
from datetime import timedelta, datetime
import sqlalchemy as db


async def register_student(telegram_id: str, student_id: str, last_name: str, first_name: str, language: bool) -> None:
    async with async_session_maker() as session:
        new_student = Student(
            telegram_id=telegram_id, 
            student_id=int(student_id),
            last_name=last_name, 
            first_name=first_name,
            language=language,
            points=0
        )
        session.add(new_student)
        await session.commit()


async def get_userdata(telegram_id: int):
    async with async_session_maker() as session:
        query_select = db.select(Student).where(Student.telegram_id == telegram_id)
        result = await session.execute(query_select)
        user_data = result.scalars().first()  # Извлечение первой записи (или None, если записи нет)
        if user_data is None:
            return False
        return user_data


async def get_pair_info(id: int):
    pass

async def update_language(telegram_id: int) -> None:
    async with async_session_maker() as session:
        query_update = (
            update(Student)
            .where(Student.telegram_id == telegram_id)
            .values(language = ~Student.language)
        )
        await session.execute(query_update)
        await session.commit()

async def update_firstname(telegram_id: int, first_name: str) -> None:
    async with async_session_maker() as session:
        query_update = (
            update(Student)
            .where(Student.telegram_id == telegram_id)
            .values(first_name=first_name)
        )
        await session.execute(query_update)
        await session.commit()

async def update_lastname(telegram_id: int, last_name: str) -> None:
    async with async_session_maker() as session:
        query_update = (
            update(Student)
            .where(Student.telegram_id == telegram_id)
            .values(last_name=last_name)
        )
        await session.execute(query_update)
        await session.commit()

async def update_studentid(telegram_id: int, student_id: str) -> None:
    async with async_session_maker() as session:
        query_update = (
            update(Student)
            .where(Student.telegram_id == telegram_id)
            .values(student_id=int(student_id))
        )
        await session.execute(query_update)
        await session.commit()

# Баллы начисляю автоматически. На случай, если Хонер-Телефон начнёт докапываться, мол,
# у вас только обертка без БДшки
async def sign_up_to_section(telegram_id: int, student_id: int) -> None:
    async with async_session_maker() as session:
        async with session.begin():
            new_record = Records(
                student_id=student_id,
                pair_id=0
            )
            session.add(new_record)
            query_update = (
                update(Student)
                .where(Student.telegram_id == telegram_id)
                .values(points = Student.points+10)
            )
            await session.execute(query_update)


async def unsign(student_id: int) -> None: # Пока не работает и не используется!
    async with async_session_maker() as session:
        query_update = (
            delete(Records)
            .where(Records.id == student_id)
            .values(free_slots_left=Schedule.free_slots_left + 1)
        )
        await session.execute(query_update)
        await session.commit()