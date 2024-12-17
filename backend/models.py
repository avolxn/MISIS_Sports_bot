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
    first_name = Column(String()) 
    last_name = Column(String()) 
    patronymic = Column(String(), default=None) 
    points = Column(Integer(), default = 0) 
    language = Column(Integer(), default = 0) 
    def __repr__(self): 
        return f"Student(telegramid='{self.telegram_id}', studentid='{self.student_id}', lastname='{self.last_name}', firstname='{self.first_name}')" 
 
class Coach(Base): 
    __tablename__ = "coaches" 
    id = Column(BigInteger(), primary_key=True, autoincrement=True) 
    telegram_id = Column(BigInteger(), default=None) 
    first_name = Column(String()) 
    last_name = Column(String()) 
    patronymic = Column(String(), default=None) 
    is_approved = Column(Boolean(), default=False) 
    secret_token = Column(String(), default=None) 
 
 
class CoachToGym(Base): 
    __tablename__ = 'coaches_to_gyms' 
    id = Column(Integer(), primary_key=True, autoincrement=True) 
    coach = Column(ForeignKey("coaches.id")) 
    gym = Column(Integer()) 
 
 
class Schedule(Base): 
    __tablename__ = "schedule" 
    id = Column(BigInteger(), primary_key=True) 
    date = Column(DateTime()) 
    pair = Column(Integer()) 
    gym = Column(Integer()) 
    coach = Column(ForeignKey("coaches.id")) 
    free_places_left = Column(Integer()) 
     
 
class Records(Base): 
    __tablename__ = "records" 
    id = Column(BigInteger(), primary_key=True, autoincrement=True) 
    student_id = Column(BigInteger()) 
    pair_id = Column(ForeignKey("schedule.id")) 
    approved = Column(Boolean(), default=False)