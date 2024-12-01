from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Здесь через КЛАССЫ описываются все таблички, их соответсвенно тоже нужно переделать
# Кстати, типы полей в postgresql отличаются от тех, что есть в sqlite, тоже имей ввиду
# Один класс я уже оформил для примера, другие же модели я отправил в группу (там фотки с табличками)

class Student(Base):
    __tablename__ = "users"
    telegram_id = Column(BigInteger(), primary_key=True)
    student_id = Column(BigInteger())
    last_name = Column(String())
    first_name = Column(String())
    points = Column(Integer(), default = 0)
    is_english = Column(Boolean())
    def __repr__(self):
        return f"Student(telegramid='{self.telegram_id}', studentid='{self.student_id}', lastname='{self.last_name}', firstname='{self.first_name}')"


class Schedule(Base):
    __tablename__ = "pairs"
    id = Column(BigInteger(), primary_key=True)
    date = Column(DateTime())
    pair = Column(Integer())
    gym = Column(Integer())
    free_slots_left = Column(Integer(), default = 30)
    def __repr__(self):
        return f"Pair(id='{self.id}', date='{self.date}', pair='{self.pair}', capacity='{self.free_slots_left}')"