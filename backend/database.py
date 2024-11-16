import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from .models import *
from .cors import *

engine = db.create_engine('sqlite:///data.db')
conn = engine.connect()
metadata = db.MetaData()

Session = sessionmaker(bind=engine)
session = Session()

students = db.Table('students', metadata, autoload_with=engine)
schedule = db.Table('schedule', metadata, autoload_with=engine)


def update_userdata(telegram_id: str) -> None:
    query = db.select(students).where(students.c.telegram_id == telegram_id)
    result = conn.execute(query).fetchall()
    if result:
        return result[0][1], result[0][2], result[0][3], result[0][4]
    else:
        return False, False, False, False


def register_student(telegram_id: str, student_id: str, last_name: str, first_name: str) -> None:
    #Проверка, есть ли уже студент с этим ID
    query = db.select(students).where(students.c.telegram_id == telegram_id) 
    result = conn.execute(query)

    if result.fetchall(): # Изменение уже существующих данных, если студент уже есть в БД
        session.query(students).filter(students.c.telegram_id == telegram_id).update({
            'last_name': last_name,
            'first_name': first_name,
            'student_id': student_id
        })
        session.commit()
    else: # Иначе добавляем его в БД
        insertion_query = students.insert().values([{
            'telegram_id': telegram_id,
            'student_id': student_id, 
            'last_name': last_name, 
            'first_name': first_name,
            'points': 0
        }])
        conn.execute(insertion_query)
        conn.commit()


def sign_up_to_class(student_id: str, points: int) -> None:
    query = db.select(students).where(students.c.student_id == student_id)
    result = conn.execute(query)


def main() -> None:
    query = db.select(students)
    result = conn.execute(query)
    print(result.fetchall())


if __name__ == "__main__":
    main()
