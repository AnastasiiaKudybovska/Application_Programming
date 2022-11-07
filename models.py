from sqlalchemy import create_engine, Column, Integer, String,  orm, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base, backref

DB_URI = "mysql+pymysql://root:1307ak@localhost:3306/student_rating"

engine = create_engine(DB_URI)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

BaseModel = declarative_base()


class User(BaseModel):
    __tablename__ = "user"
    id_user = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True, nullable=False)
    password = Column(String(512), nullable=False)
    first_name = Column(String(25), nullable=False)
    last_name = Column(String(25), nullable=False)
    email = Column(String(45), nullable=False)
    phone = Column(String(25))


class Group(BaseModel):
    __tablename__ = "group"
    id_group = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False)


class Student(BaseModel):
    __tablename__ = "student"
    user_id = Column(Integer, ForeignKey(User.id_user, ondelete='CASCADE'), primary_key=True, autoincrement=True)
    user = orm.relationship(User, uselist=False, passive_deletes=True)
    date_of_birthday = Column(Date, nullable=False)
    date_of_entry = Column(Date, nullable=False)
    date_of_graduation = Column(Date, nullable=False)
    group_id = Column(Integer, ForeignKey(Group.id_group, ondelete='CASCADE'))
    group = orm.relationship(Group, backref=backref("student", cascade="all, delete"))


class Teacher(BaseModel):
    __tablename__ = "teacher"
    user_id = Column(Integer, ForeignKey(User.id_user, ondelete='CASCADE'), primary_key=True, autoincrement=True)
    user = orm.relationship(User, uselist=False, passive_deletes=True)
    date_of_employment = Column(Date, nullable=False)
    qualification = Column(String(75), nullable=False)


class Subject(BaseModel):
    __tablename__ = "subject"
    id_subject = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    credits = Column(Integer, nullable=False)


class Mark(BaseModel):
    __tablename__ = "mark"
    id_mark = Column(Integer, primary_key=True)
    mark = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id_subject, ondelete='CASCADE'))
    subject = orm.relationship(Subject, backref=backref("mark", cascade="all, delete"))
    student_id = Column(Integer, ForeignKey(Student.user_id,  ondelete='CASCADE'))
    student = orm.relationship(Student, backref=backref("mark", cascade="all, delete"))
    teacher_id = Column(Integer, ForeignKey(Teacher.user_id, ondelete='SET NULL'))
    teacher = orm.relationship(Teacher, backref="mark")