from typing import Union
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import insert, select, and_, update, delete
from backend.models import Student, Schedule, Records, Coach, CoachToGym
from backend.database import async_session_maker
from datetime import timedelta, datetime
import sqlalchemy as db


async def register_student(
    telegram_id: str, student_id: str, last_name: str, first_name: str, language: int
) -> None:
    """
    Создаём запись студента
    """
    async with async_session_maker() as session:
        new_student = Student(
            telegram_id=telegram_id,
            student_id=int(student_id),
            last_name=last_name,
            first_name=first_name,
            language=language,
            points=0,
        )
        session.add(new_student)
        await session.commit()


async def get_userdata(telegram_id: int) -> Union[Student, bool]:
    """
    Получаем данные студента по тг айди
    """
    async with async_session_maker() as session:
        query_select = db.select(Student).where(Student.telegram_id == telegram_id)
        result = await session.execute(query_select)
        user_data = (
            result.scalars().first()
        )  # Извлечение первой записи (или None, если записи нет)
        if user_data is None:
            return False
        return user_data


async def get_userdata_by_student_id(student_id: int) -> Union[Student, bool]:
    """
    Получаем данные студента по студенческому айди
    """
    async with async_session_maker() as session:
        query_select = db.select(Student).where(Student.student_id == student_id)
        result = await session.execute(query_select)
        user_data = (
            result.scalars().first()
        )  # Извлечение первой записи (или None, если записи нет)
        if user_data is None:
            return False
        return user_data


async def get_unapproved_signups(pair: int, gym: int, date: datetime) -> None:
    """
    Получаем неподтверждённые записи на пару
    """
    pair_id = await get_pair_id(pair=pair, gym=gym, date=date)
    async with async_session_maker() as session:
        query_select = db.select(Records).where(
            (Records.approved == False) & (Records.pair_id == pair_id)
        )
        result = await session.execute(query_select)
        signups = result.scalars()
        return signups


async def get_pair_id(pair: int, gym: int, date: datetime) -> int:
    """
    Получаем пару по залу, дате и номеру пары
    """
    async with async_session_maker() as session:
        query_select = db.select(Schedule).where(
            (Schedule.pair == pair) & (Schedule.gym == gym) & (Schedule.date == date)
        )
        result = await session.execute(query_select)
        signups = result.scalars().first()
        return signups.id


async def approve_signup(id: int, student_id: int) -> None:
    """
    Подтверждаем запись на пару и обновляем счётчик баллов на 10
    """
    async with async_session_maker() as session:
        async with session.begin():
            query_update = update(Records).where(Records.id == id).values(approved=True)
            await session.execute(query_update)
            query_update = (
                update(Student)
                .where(Student.student_id == student_id)
                .values(points=Student.points + 10)
            )
            await session.execute(query_update)


async def update_language(telegram_id: int, language: int) -> None:
    """
    Изменяем язык для интерфейса студента
    """
    async with async_session_maker() as session:
        query_update = (
            update(Student)
            .where(Student.telegram_id == telegram_id)
            .values(language=language)
        )
        await session.execute(query_update)
        await session.commit()


async def update_firstname(telegram_id: int, first_name: str) -> None:
    """
    Обновляем имя
    """
    async with async_session_maker() as session:
        query_update = (
            update(Student)
            .where(Student.telegram_id == telegram_id)
            .values(first_name=first_name)
        )
        await session.execute(query_update)
        await session.commit()


async def update_lastname(telegram_id: int, last_name: str) -> None:
    """
    Обновляем фамилию
    """
    async with async_session_maker() as session:
        query_update = (
            update(Student)
            .where(Student.telegram_id == telegram_id)
            .values(last_name=last_name)
        )
        await session.execute(query_update)
        await session.commit()


async def update_studentid(telegram_id: int, student_id: str) -> None:
    """
    Обновляем студенческий айди
    """
    async with async_session_maker() as session:
        query_update = (
            update(Student)
            .where(Student.telegram_id == telegram_id)
            .values(student_id=int(student_id))
        )
        await session.execute(query_update)
        await session.commit()


async def sign_up_to_section(
    telegram_id: int, student_id: int, pair: int, gym: int, date: datetime
):
    """
    Проверяем записан ли уже студент на пару и записываем, если нет
    """
    pair_id = await get_pair_id(pair=pair, gym=gym, date=date)
    async with async_session_maker() as session:
        async with session.begin():
            query_select = db.select(Records).where(
                (Records.pair_id == pair_id) & (Records.student_id == student_id)
            )
            result = await session.execute(query_select)
            if result.scalars().first():
                return False

            new_record = Records(student_id=student_id, pair_id=pair_id)
            session.add(new_record)
            await session.flush()
            return new_record.id


async def unsign(record_id: int) -> None:
    """
    Оменяеи запись на пару
    """
    async with async_session_maker() as session:
        query_update = delete(Records).where(Records.id == record_id)
        await session.execute(query_update)
        await session.commit()


async def get_coach(telegram_id: str):
    """
    Получаем тренера по тг айди
    """
    async with async_session_maker() as session:
        query_select = db.select(Coach).where(Coach.telegram_id == int(telegram_id))
        result = await session.execute(query_select)
        coach_data = result.scalars().first()
        if coach_data is None:
            return False
        return coach_data


async def get_coach_by_secret(secret_token: str):
    """
    Получаем тренера по секретному токену
    """
    async with async_session_maker() as session:
        query_select = db.select(Coach).where(Coach.secret_token == secret_token)
        result = await session.execute(query_select)
        coach_data = result.scalars().first()
        if coach_data is None:
            return False
        return coach_data


async def verify_secret(id: int, telegram_id: str):
    """
    Проверяем совпадает ли секретный токен тренера
    """
    async with async_session_maker() as session:
        query_update = (
            db.update(Coach)
            .where(Coach.id == id)
            .values(telegram_id=int(telegram_id), is_approved=True)
        )
        await session.execute(query_update)
        await session.commit()


async def register_coach(
    first_name: str, last_name: str, patronymic: str, secret_token: str = None
):
    """
    Регистрируем тренера
    """
    async with async_session_maker() as session:
        new_coach = Coach(
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            secret_token=secret_token,
        )
        session.add(new_coach)
        await session.commit()
        return new_coach.id


async def register_coaches_to_gyms(telegram_id: str, gyms: list) -> None:
    """
    Записываем связь между тренером и залами
    """
    async with async_session_maker() as session:
        for i in range(len(gyms)):
            if gyms[i]:
                new_coach_to_gym = CoachToGym(coach=int(telegram_id), gym=i)
                session.add(new_coach_to_gym)
                await session.commit()


async def get_coach_gyms(telegram_id: str):
    """
    Получаем доступные тренеру залы
    """
    async with async_session_maker() as session:
        coach = await get_coach(telegram_id)
        query_select = db.select(CoachToGym).where(CoachToGym.coach == coach.id)
        result = (await session.execute(query_select)).all()
        return result
