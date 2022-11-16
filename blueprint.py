import operator

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, unset_jwt_cookies, jwt_required
from marshmallow import ValidationError, EXCLUDE
from db_utils import create_entry, update_entry
from models import Session, User, Subject, Group, Teacher, Student, Mark
from resp_error import errors
from schemas import UserSchema, SubjectSchema, SubjectData, GroupSchema, GroupData, TeacherData, \
    TeacherAllData, TeacherDataToUpdate, StudentData, StudentAllData, StudentDataToUpdate, MarkSchema, MarkAllData, \
    MarkData, MarkToTeacherUpdate, MarkToTeacherPost, UserData, UserLogin

api_blueprint = Blueprint('api', __name__)

session = Session()


@api_blueprint.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    if User.is_admin():
        users_list = session.query(User).all()
        return UserData().dump(users_list, many=True), 200
    return errors.no_access


#  ###### USER AUTHENTICATION AND AUTHORIZATION ######

@api_blueprint.route('/sign-up/teacher', methods=['POST'])
def t_signup():
    json_data = request.json
    if not json_data:
        return errors.bad_request
    try:
        user_data = UserSchema(unknown=EXCLUDE).load(json_data)
        date_of_employment = json_data['date_of_employment']
        qualification = json_data['qualification']
    except ValidationError as err:
        return err.messages, 422
    user = session.query(User).filter_by(username=user_data["username"]).first()
    if user:
        return errors.exists
    user = create_entry(User, **user_data)
    teacher = Teacher(user_id=user.id_user, date_of_employment=date_of_employment, qualification=qualification)
    session.add(teacher)
    session.commit()
    token = user.create_token()
    return {'access_token': token}


@api_blueprint.route('/sign-up/student', methods=['POST'])
def st_signup():
    json_data = request.json
    if not json_data:
        return errors.bad_request
    try:
        user_data = UserSchema(unknown=EXCLUDE).load(json_data)
        date_of_birthday = json_data['date_of_birthday']
        date_of_entry = json_data['date_of_entry']
        date_of_graduation = json_data['date_of_graduation']
        group_id = json_data['group_id']
    except ValidationError as err:
        return err.messages, 422
    user = session.query(User).filter_by(username=user_data["username"]).first()
    if user:
        return errors.exists
    user = create_entry(User, **user_data)
    student = Student(user_id=user.id_user, date_of_birthday=date_of_birthday, date_of_entry=date_of_entry,
                      date_of_graduation=date_of_graduation, group_id=group_id)
    session.add(student)
    session.commit()
    token = user.create_token()
    return {'access_token': token}


@api_blueprint.route('/login', methods=['POST'])
def login():
    json_data = request.json
    if not json_data:
        return errors.bad_request
    try:
        user_data = UserLogin().load(json_data)
    except ValidationError as err:
        return err.messages, 422
    user = User.authenticate(user_data['username'], user_data['password'])
    token = user.create_token()
    return {'access_token': token}


@api_blueprint.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200


@api_blueprint.route('/user/<string:username>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def user_username_api(username):
    user = session.query(User).filter_by(username=username).first()
    if not user:
        return errors.not_found
    if request.method == 'GET':
        return UserData().dump(user), 200
    curr_user = get_jwt_identity()
    if request.method == 'PUT':
        if user.id_user != curr_user:
            return errors.no_access
        json_data = request.json
        if not json_data:
            return errors.bad_request
        try:
            data = UserSchema().load(json_data, partial=True)
        except ValidationError as err:
            return err.messages, 422
        for key, value in data.items():
            if key == "username":
                us = session.query(User).filter_by(username=data["username"]).first()
                if us:
                    return errors.exists
        updated_user = update_entry(user, **data)
        for key, value in data.items():
            if key == "password" and len(data) == 1:
                return {"message": "Password changed successfully"}, 200
        return UserData().dump(updated_user), 200
    if request.method == 'DELETE':
        if user.id_user != curr_user:
            return errors.no_access
        session.delete(user)
        session.commit()
        return {"message": "Deleted successfully"}, 200


#  ###### SUBJECT ######
@api_blueprint.route("/subjects", methods=["POST", "GET"])
@jwt_required()
def subject_api():
    if request.method == 'POST':  # check admin rights
        if User.is_admin():
            json_data = request.json
            if not json_data:
                return errors.bad_request
            try:
                subject_data = SubjectSchema().load(json_data)
            except ValidationError as err:
                return err.messages, 422
            new_subject = create_entry(Subject, **subject_data)
            return jsonify(SubjectData().dump(new_subject))
        return errors.no_access
    if request.method == 'GET':
        subject_list = session.query(Subject).all()
        return SubjectData().dump(subject_list, many=True), 200


@api_blueprint.route('/subjects/<int:subjectId>', methods=['GET', 'PUT', 'DELETE'])  # admin rights
@jwt_required()
def subject_id_api(subjectId):
    sub = session.query(Subject).filter_by(id_subject=subjectId).first()
    if not sub:
        return errors.not_found
    if request.method == 'GET':
        return SubjectData().dump(sub)
    if User.is_admin():
        if request.method == 'PUT':
            json_data = request.json
            if not json_data:
                return errors.bad_request
            try:
                data = SubjectSchema().load(json_data, partial=True)
            except ValidationError as err:
                return err.messages, 422
            updated_subject = update_entry(sub, **data)
            return SubjectData().dump(updated_subject)
        if request.method == 'DELETE':
            session.delete(sub)
            session.commit()
            return {"message": "Deleted successfully"}, 200
    return errors.no_access


#  ###### GROUP ######
@api_blueprint.route("/groups", methods=["POST", "GET"])  # post admin
@jwt_required()
def group_api():
    if request.method == 'POST':
        if User.is_admin():
            json_data = request.json
            if not json_data:
                return errors.bad_request
            try:
                group_data = GroupSchema().load(json_data)
            except ValidationError as err:
                return err.messages, 422
            new_group = session.query(Group).filter_by(name=group_data["name"]).first()
            if new_group:
                return errors.exists
            new_group = create_entry(Group, **group_data)
            return jsonify(GroupData().dump(new_group))
        return errors.no_access
    if request.method == 'GET':
        group_list = session.query(Group).all()
        return GroupData().dump(group_list, many=True), 200


@api_blueprint.route('/groups/<int:groupId>', methods=['GET', 'PUT', 'DELETE'])  # admin put delete
@jwt_required()
def group_id_api(groupId):
    gr = session.query(Group).filter_by(id_group=groupId).first()
    if not gr:
        return errors.not_found
    if request.method == 'GET':
        return GroupData().dump(gr)
    if User.is_admin():
        if request.method == 'PUT':
            json_data = request.json
            if not json_data:
                return errors.bad_request
            try:
                data = GroupSchema().load(json_data, partial=True)
            except ValidationError as err:
                return err.messages, 422
            updated_group = session.query(Group).filter_by(name=data["name"]).first()
            if updated_group:
                return errors.exists
            updated_group = update_entry(gr, **data)
            return GroupData().dump(updated_group)
        if request.method == 'DELETE':
            session.delete(gr)
            session.commit()
            return {"message": "Deleted successfully"}, 200
    return errors.no_access


#  ###### TEACHER ######
@api_blueprint.route("/teachers", methods=["GET"])
@jwt_required()
def teacher_api():
    if request.method == 'GET':
        teacher_list = session.query(Teacher).all()
        return TeacherAllData().dump(teacher_list, many=True), 200


@api_blueprint.route('/teachers/<int:teacherId>', methods=['GET', 'PUT', 'DELETE'])  # оце дивно
@jwt_required()
def teacher_id_api(teacherId):
    teacher = session.query(Teacher).filter_by(user_id=teacherId).first()
    if not teacher:
        return errors.not_found
    curr_user = get_jwt_identity()
    if teacherId != curr_user:
        return errors.no_access
    if request.method == 'GET':
        return TeacherAllData().dump(teacher)
    if request.method == 'PUT':
        json_data = request.json
        if not json_data:
            return errors.bad_request
        try:
            data = TeacherDataToUpdate().load(json_data, partial=True)
        except ValidationError as err:
            return err.messages, 422
        updated_teacher = update_entry(teacher, **data)
        return TeacherAllData().dump(updated_teacher)
    if request.method == 'DELETE':
        session.delete(teacher)
        session.commit()
        return {"message": "Deleted successfully"}, 200


@api_blueprint.route('/teachers/<int:teacherId>/marks', methods=["GET"])
@jwt_required()
def teacher_id_marks_api(teacherId):
    teacher = session.query(Teacher).filter_by(user_id=teacherId).first()
    curr_user = get_jwt_identity()
    if not teacher:
        return errors.not_found
    if teacherId != curr_user:
        return errors.no_access
    mark_list = session.query(Mark).filter_by(teacher_id=teacherId).all()
    return MarkData().dump(mark_list, many=True), 200


@api_blueprint.route('/teachers/<int:teacherId>/subjects/<int:subjectId>/marks', methods=["GET"])
@jwt_required()
def teacher_id_subject_id_marks_api(teacherId, subjectId):
    teacher = session.query(Teacher).filter_by(user_id=teacherId).first()
    subject = session.query(Subject).filter_by(id_subject=subjectId).first()
    if not teacher or not subject:
        return errors.not_found
    curr_user = get_jwt_identity()
    if teacherId != curr_user:
        return errors.no_access
    mark_list = session.query(Mark).filter_by(teacher_id=teacherId, subject_id=subjectId).all()
    return MarkData().dump(mark_list, many=True), 200


@api_blueprint.route('/teachers/<int:teacherId>/subjects/<int:subjectId>/students/<int:studentId>/marks',
                     methods=['GET', 'POST'])
@jwt_required()
def teacher_id_subject_id_student_id_marks_api(teacherId, subjectId, studentId):
    teacher = session.query(Teacher).filter_by(user_id=teacherId).first()
    subject = session.query(Subject).filter_by(id_subject=subjectId).first()
    student = session.query(Student).filter_by(user_id=studentId).first()
    if not teacher or not subject or not student:
        return errors.not_found
    curr_user = get_jwt_identity()
    if teacherId != curr_user:
        return errors.no_access
    if request.method == 'POST':
        json_data = request.json
        if not json_data:
            return errors.bad_request
        try:
            mark_data = MarkToTeacherPost().load(json_data)
        except ValidationError as err:
            return err.messages, 422
        mark_data.update({"subject_id": subjectId})
        mark_data.update({"student_id": studentId})
        mark_data.update({"teacher_id": teacherId})
        new_mark = create_entry(Mark, **mark_data)
        return jsonify(MarkAllData().dump(new_mark))
    if request.method == 'GET':
        mark_list = session.query(Mark).filter_by(teacher_id=teacherId, subject_id=subjectId,
                                                  student_id=studentId).all()
        return MarkData().dump(mark_list, many=True), 200


@api_blueprint.route('/teachers/<int:teacherId>/subjects/<int:subjectId>/students/<int:studentId>/marks/<int:markId>',
                     methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def teacher_id_subject_id_student_id_marks_id_api(teacherId, subjectId, studentId, markId):
    mark = session.query(Mark).filter_by(id_mark=markId, subject_id=subjectId, student_id=studentId,
                                         teacher_id=teacherId).first()
    curr_user = get_jwt_identity()
    if teacherId != curr_user:
        return errors.no_access
    if not mark:
        return errors.not_found
    if request.method == 'GET':
        return MarkAllData().dump(mark), 200
    if request.method == 'PUT':
        json_data = request.json
        if not json_data:
            return errors.bad_request
        try:
            data = MarkToTeacherUpdate().load(json_data, partial=True)
        except ValidationError as err:
            return err.messages, 422
        for key, value in data.items():
            if key == "subject_id":
                mark_subj = session.query(Subject).filter_by(id_subject=data["subject_id"]).first()
                if not mark_subj:
                    return {'error': {'code': 404,
                                      'message': 'Not found subject with this id'}}, 404
            elif key == "student_id":
                mark_st = session.query(Student).filter_by(user_id=data["student_id"]).first()
                if not mark_st:
                    return {'error': {'code': 404, 'message': 'Not found student with this id'}}, 404
        data.update({"teacher_id": teacherId})
        updated_mark = update_entry(mark, **data)
        return MarkAllData().dump(updated_mark)
    if request.method == 'DELETE':
        session.delete(mark)
        session.commit()
        return {"message": "Deleted successfully"}, 200


#  ###### STUDENT ######
@api_blueprint.route("/students", methods=["POST", "GET"])
@jwt_required()
def student_api():
    if request.method == 'POST':
        if User.is_admin():
            json_data = request.json
            if not json_data:
                return errors.bad_request
            try:
                student_data = StudentData().load(json_data)
            except ValidationError as err:
                return err.messages, 422
            st_user = session.query(User).filter_by(id_user=student_data["user_id"]).first()
            if not st_user:
                return {'error': {'code': 404, 'message': 'Not found user with this id'}}, 404
            st = session.query(Student).filter_by(user_id=student_data["user_id"]).first()
            if st:
                return errors.exists
            for key, value in student_data.items():
                if key == "group_id":
                    st_group = session.query(Group).filter_by(id_group=student_data["group_id"]).first()
                    if not st_group:
                        return {'error': {'code': 404, 'message': 'Not found group with this id'}}, 404
            new_student = create_entry(Student, **student_data)
            return jsonify(StudentAllData().dump(new_student))
        else:
            return errors.no_access
    if request.method == 'GET':
        student_list = session.query(Student).all()
        return StudentAllData().dump(student_list, many=True), 200


@api_blueprint.route('/students/<int:studentId>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def student_id_api(studentId):
    student = session.query(Student).filter_by(user_id=studentId).first()
    if not student:
        return errors.not_found
    curr_user = get_jwt_identity()
    if studentId != curr_user:
        return errors.no_access
    if request.method == 'GET':
        return StudentAllData().dump(student)
    if request.method == 'PUT':
        json_data = request.json
        if not json_data:
            return errors.bad_request
        try:
            data = StudentDataToUpdate().load(json_data, partial=True)
        except ValidationError as err:
            return err.messages, 422
        for key, value in data.items():
            if key == "group_id":
                new_gr_student = session.query(Group).filter_by(id_group=data["group_id"]).first()
                if not new_gr_student:
                    return {'error': {'code': 404, 'message': 'Not found group with this id'}}, 404
        updated_student = update_entry(student, **data)
        return StudentAllData().dump(updated_student)
    if request.method == 'DELETE':
        session.delete(student)
        session.commit()
        return {"message": "Deleted successfully"}, 200


@api_blueprint.route('/students/<int:studentId>/marks', methods=["GET"])
@jwt_required()
def student_id_marks_api(studentId):
    student = session.query(Student).filter_by(user_id=studentId).first()
    if not student:
        return errors.not_found
    curr_user = get_jwt_identity()
    if studentId != curr_user:
        return errors.no_access
    mark_list = session.query(Mark).filter_by(student_id=studentId).all()
    return MarkData().dump(mark_list, many=True), 200


@api_blueprint.route('/students/<int:studentId>/marks/<int:markId>', methods=["GET"])
@jwt_required()
def student_id_marks_id_api(studentId, markId):
    mark = session.query(Mark).filter_by(id_mark=markId, student_id=studentId).first()
    if not mark:
        return errors.not_found
    curr_user = get_jwt_identity()
    if studentId != curr_user:
        return errors.no_access
    return MarkAllData().dump(mark), 200


@api_blueprint.route('/students/<int:studentId>/subjects/<int:subjectId>/marks', methods=["GET"])
@jwt_required()
def student_id_subject_id_marks_api(studentId, subjectId):
    student = session.query(Student).filter_by(user_id=studentId).first()
    subject = session.query(Subject).filter_by(id_subject=subjectId).first()
    if not student or not subject:
        return errors.not_found
    curr_user = get_jwt_identity()
    if studentId != curr_user:
        return errors.no_access
    mark_list = session.query(Mark).filter_by(student_id=studentId, subject_id=subjectId).all()
    return MarkData().dump(mark_list, many=True), 200


@api_blueprint.route('/students/rating', methods=["GET"])
def rating():
    st_rating = {}
    student_list = session.query(Student).all()
    for student in student_list:
        subject_credits = 1
        sum_mark = 0
        sum_credits = 1
        k = 1
        s = StudentData().dump(student)
        mark_list = session.query(Mark).filter_by(student_id=s["user_id"]).all()
        for mark in mark_list:
            m = MarkSchema().dump(mark)
            for key, value in m.items():
                if key == "subject_id":
                    subject = session.query(Subject).filter_by(id_subject=value).first()
                    subject_credits = subject.credits
                    sum_credits += subject_credits
            sum_mark += m["mark"] * subject_credits
            k = sum_mark / len(mark_list)
        r_mark = k * 1.25 * sum_credits
        st_rating.update({student: r_mark})
    sort_st = sorted(st_rating.items(), key=operator.itemgetter(1), reverse=True)
    return StudentData().dump(dict(sort_st), many=True), 200


#  ###### MARKS ######
@api_blueprint.route("/marks", methods=["POST", "GET"])
@jwt_required()
def marks_api():
    if request.method == 'POST':
        json_data = request.json
        if not json_data:
            return errors.bad_request
        try:
            mark_data = MarkSchema().load(json_data)
        except ValidationError as err:
            return err.messages, 422
        mark_subj = session.query(Subject).filter_by(id_subject=mark_data["subject_id"]).first()
        if not mark_subj:
            return {'error': {'code': 404,
                              'message': 'Not found subject with this id'}}, 404
        mark_st = session.query(Student).filter_by(user_id=mark_data["student_id"]).first()
        if not mark_st:
            return {'error': {'code': 404,
                              'message': 'Not found student with this id'}}, 404
        mark_th = session.query(Teacher).filter_by(user_id=mark_data["teacher_id"]).first()
        if not mark_th:
            return {'error': {'code': 404,
                              'message': 'Not found teacher with this id'}}, 404
        if mark_th.user_id != get_jwt_identity():
            return errors.no_access
        if mark_data["teacher_id"] == mark_data["student_id"]:
            return {'error': {'code': 400,
                              'message': 'Invalid request. Teacher_id and student_id must be different'}}, 400
        new_mark = create_entry(Mark, **mark_data)
        return jsonify(MarkData().dump(new_mark))
    if request.method == 'GET':
        user = get_jwt_identity()
        mark_list = session.query(Mark).filter_by(teacher_id=user).all()
        if not mark_list:
            mark_list = session.query(Mark).filter_by(student_id=user).all()
        return MarkData().dump(mark_list, many=True), 200


@api_blueprint.route('/marks/<int:markId>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def marks_id_api(markId):
    mark = session.query(Mark).filter_by(id_mark=markId).first()
    if not mark:
        return errors.not_found
    user = get_jwt_identity()
    if user != mark.teacher_id and user != mark.student_id:
        return errors.no_access
    if request.method == 'GET':
        return MarkData().dump(mark)
    if request.method == 'PUT':
        if user != mark.teacher_id:
            return errors.no_access
        json_data = request.json
        if not json_data:
            return errors.bad_request
        try:
            data = MarkSchema().load(json_data, partial=True)
        except ValidationError as err:
            return err.messages, 422
        mark_subj = session.query(Subject).filter_by(id_subject=data["subject_id"]).first()
        if not mark_subj:
            return {'error': {'code': 404,
                              'message': 'Not found subject with this id'}}, 404
        mark_st = session.query(Student).filter_by(user_id=data["student_id"]).first()
        if not mark_st:
            return {'error': {'code': 404,
                              'message': 'Not found student with this id'}}, 404
        mark_th = session.query(Teacher).filter_by(user_id=data["teacher_id"]).first()
        if not mark_th:
            return {'error': {'code': 404,
                              'message': 'Not found teacher with this id'}}, 404
        if data["teacher_id"] == data["student_id"]:
            return {'error': {'code': 400,
                              'message': 'Invalid request. Teacher_id and student_id must be different'}}, 400
        updated_mark = update_entry(mark, **data)
        return MarkData().dump(updated_mark)
    if request.method == 'DELETE':
        if user != mark.teacher_id:
            return errors.no_access
        session.delete(mark)
        session.commit()
        return {"message": "Deleted successfully"}, 200
