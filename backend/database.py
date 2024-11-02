import sqlalchemy as db

engine = db.create_engine('sqlite:///data.db')
conn = engine.connect()
metadata = db.MetaData()

students = db.Table('students', metadata, autoload_with=engine)
schedule = db.Table('schedule', metadata, autoload_with=engine)

def add_new_student(student_id: str, last_name: str, first_name: str, second_name: str) -> None:
    insertion_query = students.insert.values([
        {
            'student_id': student_id, 
            'last_name': last_name, 
            'first_name': first_name, 
            'second_name': second_name, 
            'points': 0
        }
    ])
    conn.execute(insertion_query)
    conn.commit()

def add_points(student_id: str, points: int) -> None:
    query = db.select(students).where(students.c.student_id == student_id)
    result = conn.execute(query)