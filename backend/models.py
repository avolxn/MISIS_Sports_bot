from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    BigInteger,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Student(Base):
    """
    Таблица со студентами
    """

    __tablename__ = "users"
    telegram_id = Column(BigInteger(), primary_key=True)
    student_id = Column(BigInteger())
    first_name = Column(String())
    last_name = Column(String())
    patronymic = Column(String(), default=None)
    points = Column(Integer(), default=0)
    language = Column(Integer(), default=0)


class Coach(Base):
    """
    Таблица с тренерами
    """

    __tablename__ = "coaches"
    id = Column(BigInteger(), primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger(), default=None)
    first_name = Column(String())
    last_name = Column(String())
    patronymic = Column(String(), default=None)
    is_approved = Column(Boolean(), default=False)
    secret_token = Column(String(), default=None)


class CoachToGym(Base):
    """
    Таблица, которая привязывает тренеров к их залам
    """

    __tablename__ = "coaches_to_gyms"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    coach = Column(ForeignKey("coaches.id"))
    gym = Column(Integer())


class Schedule(Base):
    """
    Таблица с парами, пары генерируются каждую неделю в субботу в полночь
    """

    __tablename__ = "schedule"
    id = Column(BigInteger(), primary_key=True)
    date = Column(DateTime())
    pair = Column(Integer())
    gym = Column(Integer())
    coach = Column(ForeignKey("coaches.id"))
    free_places_left = Column(Integer())


class Records(Base):
    """
    Таблица с записями на пару
    """

    __tablename__ = "records"
    id = Column(BigInteger(), primary_key=True, autoincrement=True)
    student_id = Column(BigInteger())
    pair_id = Column(ForeignKey("schedule.id"))
    approved = Column(Boolean(), default=False)
