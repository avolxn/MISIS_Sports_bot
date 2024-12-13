from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger, ForeignKey
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
    patronymic = Column(String(), default=None)
    points = Column(Integer(), default = 0)
    is_english = Column(Boolean())
    def __repr__(self):
        return f"Student(telegramid='{self.telegram_id}', studentid='{self.student_id}', lastname='{self.last_name}', firstname='{self.first_name}')"

class Coach(Base):
    __tablename__ = "coaches"
    id = Column(BigInteger(), primary_key=True)
    telegram_id = Column(BigInteger(), default=None)
    last_name = Column(String())
    first_name = Column(String())
    patronymic = Column(String(), default=None)
    is_admin = Column(Boolean(), default=False) 
    is_approved = Column(Boolean(), default=False)
    secret_token = Column(String())

class Schedule(Base):
    __tablename__ = "schedule"
    id = Column(BigInteger(), primary_key=True)
    date = Column(DateTime())
    pair = Column(Integer())
    gym = Column(Integer())
    coach = Column(ForeignKey("coaches.id"))
    free_places_left = Column(Integer())
    def __repr__(self):
        return f""
    

class Records(Base):
    __tablename__ = "records"
    id = Column(BigInteger(), primary_key=True, autoincrement=True)
    student_id = Column(BigInteger())
    pair_id = Column(BigInteger()) # Column(ForeignKey("schedule.id"))
    approved = Column(Boolean(), default=False)
    def __repr__(self):
        return f""
    
