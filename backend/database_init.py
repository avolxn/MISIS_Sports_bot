import sqlalchemy as db

engine = db.create_engine('sqlite:///data.db')
conn = engine.connect()
metadata = db.MetaData()

students = db.Table('students', metadata,
    db.Column('student_id', db.Text, primary_key=True),
    db.Column('last_name', db.Text),
    db.Column('first_name', db.Text),
    db.Column('second_name', db.Text),
    db.Column('points', db.Integer)
)
schedule = db.Table('students', metadata,
    db.Column('student_id', db.Text, primary_key=True),
    db.Column('week_day', db.Integer),
    db.Column('pair', db.Integer),
    db.Column('gym', db.Text),
)
metadata.create_all(engine)