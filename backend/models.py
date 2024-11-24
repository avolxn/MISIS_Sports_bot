from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Здесь через КЛАССЫ описываются все таблички, их соответсвенно тоже нужно переделать
# Кстати, типы полей в postgresql отличаются от тех, что есть в sqlite, тоже имей ввиду
# Один класс я уже оформил для примера, другие же модели я отправил в группу (там фотки с табличками)

class Student(Base):
    __tablename__ = "users"
    telegram_id = Column(String(), primary_key=True)
    student_id = Column(BigInteger())
    last_name = Column(String())
    first_name = Column(String())
#   patronymic = Column(String(), default = None) # Так мы же в итоге решили, что отчеСтВО нам не нужно :/
    points = Column(Integer(), default = 0)
    def __repr__(self):
        return f"Student(telegramid='{self.telegram_id}', studentid='{self.student_id}', lastname='{self.last_name}', firstname='{self.first_name}')"