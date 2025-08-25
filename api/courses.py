from flask import request, jsonify
from . import api_blueprint
from models import db, Courses
from .auth import token_required, roles_required

# Tüm dersleri listeleme (Herkes)
@api_blueprint.route('/courses', methods=['GET'])
def get_all_courses():
    courses = Courses.query.all()
    output = []
    for course in courses:
        output.append({
            'id': course.id,
            'course_code': course.course_code,
            'course_name': course.course_name,
            'credits': course.credits,
            'department_id': course.department_id,
            'professor_id': course.professor_id
        })
    return jsonify({'courses': output})

# Yeni bir ders oluşturma (Admin ve Professor)
@api_blueprint.route('/courses', methods=['POST'])
@roles_required(['Admin', 'Professor'])
def create_course(current_user):
    data = request.get_json()
    course_code = data.get('course_code')
    course_name = data.get('course_name')
    credits = data.get('credits')
    department_id = data.get('department_id')
    professor_id = data.get('professor_id')

    if not all([course_code, course_name, credits, department_id]):
        return jsonify({'error': 'Eksik bilgi girişi!!!'}), 400

    new_course = Courses(
        course_code=course_code,
        course_name=course_name,
        credits=credits,
        department_id=department_id,
        professor_id=professor_id
    )

    try:
        db.session.add(new_course)
        db.session.commit()
        return jsonify({'message': 'Ders başarıyla oluşturuldu', 'course_id': new_course.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Ders silme (Sadece Admin)
@api_blueprint.route('/courses/<int:course_id>', methods=['DELETE'])
@roles_required(['Admin'])
def delete_course(current_user, course_id):
    course = Courses.query.get_or_404(course_id)
    try:
        db.session.delete(course)
        db.session.commit()
        return jsonify({'message': 'Ders başarıyla kaldırıldı'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500