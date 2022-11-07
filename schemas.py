from datetime import date

from flask_bcrypt import generate_password_hash
from marshmallow import Schema, validate, fields


class UserData(Schema):
    id_user = fields.Integer()
    username = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.String(validate=validate.Email())
    phone = fields.String()


class UserSchema(Schema):
    username = fields.String()
    password = fields.Function(
        deserialize=lambda obj: generate_password_hash(obj), load_only=True
    )
    first_name = fields.String()
    last_name = fields.String()
    email = fields.String(validate=validate.Email())
    phone = fields.String()


class SubjectData(Schema):
    id_subject = fields.Integer()
    name = fields.String()
    credits = fields.Integer()


class SubjectSchema(Schema):
    name = fields.String()
    credits = fields.Integer()


class GroupData(Schema):
    id_group = fields.Integer()
    name = fields.String()


class GroupSchema(Schema):
    name = fields.String()


class TeacherData(Schema):
    user_id = fields.Integer()
    date_of_employment = fields.Date(validate=lambda x: x <= date.today())
    qualification = fields.String()


class TeacherAllData(Schema):
    user = fields.Nested(lambda: UserData())
    date_of_employment = fields.Date(validate=lambda x: x <= date.today())
    qualification = fields.String()


class TeacherDataToUpdate(Schema):
   # user = fields.Nested(lambda: UserSchema())
    date_of_employment = fields.Date(validate=lambda x: x <= date.today())
    qualification = fields.String()


class StudentData(Schema):
    user_id = fields.Integer()
    date_of_birthday = fields.Date(validate=lambda x: x <= date.today())
    date_of_entry = fields.Date(validate=lambda x: x <= date.today())
    date_of_graduation = fields.Date(validate=lambda x: x >= date.today())
    group_id = fields.Integer()


class StudentAllData(Schema):
    user = fields.Nested(lambda: UserData())
    date_of_birthday = fields.Date(validate=lambda x: x <= date.today())
    date_of_entry = fields.Date(validate=lambda x: x <= date.today())
    date_of_graduation = fields.Date(validate=lambda x: x >= date.today())
    group = fields.Nested(lambda: GroupData())


class StudentDataToUpdate(Schema):
    date_of_birthday = fields.Date(validate=lambda x: x <= date.today())
    date_of_entry = fields.Date(validate=lambda x: x <= date.today())
    date_of_graduation = fields.Date(validate=lambda x: x >= date.today())
    group_id = fields.Integer()


class MarkSchema(Schema):
    mark = fields.Integer()
    date = fields.Date(validate=lambda x: x <= date.today())
    subject_id = fields.Integer()
    student_id = fields.Integer()
    teacher_id = fields.Integer()


class MarkData(Schema):
    id_mark = fields.Integer()
    mark = fields.Integer()
    date = fields.Date(validate=lambda x: x <= date.today())
    subject_id = fields.Integer()
    student_id = fields.Integer()
    teacher_id = fields.Integer()


class MarkAllData(Schema):
    id_mark = fields.Integer()
    mark = fields.Integer()
    date = fields.Date(validate=lambda x: x <= date.today())
    subject = fields.Nested(lambda: SubjectData())
    student = fields.Nested(lambda: StudentAllData())
    teacher = fields.Nested(lambda: TeacherAllData())


class MarkToTeacherUpdate(Schema):
    mark = fields.Integer()
    date = fields.Date(validate=lambda x: x <= date.today())
    subject_id = fields.Integer()
    student_id = fields.Integer()


class MarkToTeacherPost(Schema):
    mark = fields.Integer()
    date = fields.Date(validate=lambda x: x <= date.today())