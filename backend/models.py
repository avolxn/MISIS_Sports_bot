from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Здесь через КЛАССЫ описываются все таблички, их соответсвенно тоже нужно переделать
# Кстати, типы полей в postgresql отличаются от тех, что есть в sqlite, тоже имей ввиду
# Один класс я уже оформил для примера, другие же модели я отправил в группу (там фотки с табличками)

class Student(Base):
    __tablename__ = "users"
    id = Column(BigInteger(), index=True, nullable=False, primary_key=True)
    student_id = Column(Integer())
    first_name = Column(String())
    last_name = Column(String())
    patronymic = Column(String(), default = None)
    points = Column(Integer(), default = 0)