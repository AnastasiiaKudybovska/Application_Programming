from models import Session, User, Group, Student, Teacher, Subject, Mark, Role

session = Session()

user1 = User(username='tim.peterson', password='1111', first_name='Tim', last_name='Peterson',
             email='timpeterson@gmail.com', phone='380974759926')
user2 = User(username='megan.rios', password='1783', first_name='Megan', last_name='Rios',
             email='meganrios@gmail.com', phone='380951806912')
user3 = User(username='t.parker.robert', password='221122', first_name='Robert', last_name='Parker',
             email='robertparker@gmail.com', phone='380737904815')
user4 = User(username='t.emily.taylor', password='331133', first_name='Emily', last_name='Taylor',
             email='emilytaylor@gmail.com', phone='380961285103')

role = session.query(Role).filter_by(id=1).first()  # admin role

user1.roles = [role]  # make user1 admin
session.add(user1)
session.add(user2)
session.add(user3)
session.add(user4)
session.commit()

group1 = Group(name='CS-215')

session.add(group1)
session.commit()

student1 = Student(user_id=user1.id_user, date_of_birthday='2004-04-18', date_of_entry='2021-09-01',
                   date_of_graduation='2025-06-25', group_id=group1.id_group)
student2 = Student(user_id=user2.id_user, date_of_birthday='2003-12-02', date_of_entry='2021-09-01',
                   date_of_graduation='2025-06-25', group_id=group1.id_group)
session.add(student1)
session.add(student2)
session.commit()

teacher1 = Teacher(user_id=user3.id_user, date_of_employment='2015-08-15',
                   qualification='Associate Professor of the AI department')
teacher2 = Teacher(user_id=user4.id_user, date_of_employment='2017-12-23',
                   qualification='Associate Professor of the FL department')

session.add(teacher1)
session.add(teacher2)
session.commit()

subject1 = Subject(name='Application Programming', credits=5)
subject2 = Subject(name='English', credits=7)

session.add(subject1)
session.add(subject2)
session.commit()

mark1 = Mark(mark=5, date='2022-10-15', subject_id=subject1.id_subject, student_id=student1.user_id,
             teacher_id=teacher1.user_id)
mark2 = Mark(mark=4, date='2022-10-12', subject_id=subject2.id_subject, student_id=student1.user_id,
             teacher_id=teacher2.user_id)
mark3 = Mark(mark=5, date='2022-10-15', subject_id=subject1.id_subject, student_id=student2.user_id,
             teacher_id=teacher1.user_id)

session.add(mark1)
session.add(mark2)
session.add(mark3)
session.commit()