import sqlalchemy as db

engine = db.create_engine('sqlite:///data.db')
conn = engine.connect()
metadata = db.MetaData()

students = db.Table('students', metadata,
    db.Column('telegram_id', db.Text, primary_key=True),
    db.Column('student_id', db.Text),
    db.Column('last_name', db.Text),
    db.Column('first_name', db.Text),
    db.Column('second_name', db.Text, nullable=True),
    db.Column('points', db.Integer)
)
schedule = db.Table('schedule', metadata,
    db.Column('telegram_id', db.Text, primary_key=True),
    db.Column('day', db.DateTime),
    db.Column('pair', db.Integer),
    db.Column('gym', db.Integer),
)
metadata.create_all(engine)