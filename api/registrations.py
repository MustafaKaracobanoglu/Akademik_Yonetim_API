from flask import request, jsonify
from . import api_blueprint
from models import db, Course_Registrations, Students, Courses
from .auth import token_required, roles_required

# Bir öğrenciyi bir derse kaydetme (Admin ve Professor)
@api_blueprint.route('/registrations', methods=['POST'])
@roles_required(['Admin', 'Professor'])
def register_course(current_user):
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')

    if not all([student_id, course_id]):
        return jsonify({'error': 'Öğrenci veya ders numarası eksik.'}), 400

    student = Students.query.get(student_id)
    course = Courses.query.get(course_id)
    if not student:
        return jsonify({'error': f'{student_id} numaralı öğrenci bulunamadı.'}), 404
    if not course:
        return jsonify({'error': f'{course_id} numaralı ders bulunamadı.'}), 404

    existing_registration = Course_Registrations.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()
    if existing_registration:
        return jsonify({'message': 'Öğrenci bu derse zaten kayıtlı.'}), 409

    new_registration = Course_Registrations(
        student_id=student_id,
        course_id=course_id
    )

    try:
        db.session.add(new_registration)
        db.session.commit()
        return jsonify({'message': 'Ders başarıyla kaydedildi'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Tüm ders kayıtlarını listeleme (Admin ve Professor)
@api_blueprint.route('/registrations', methods=['GET'])
@roles_required(['Admin', 'Professor'])
def get_all_registrations(current_user):
    registrations = Course_Registrations.query.all()
    output = []
    for reg in registrations:
        output.append({
            'id': reg.id,
            'student_id': reg.student_id,
            'course_id': reg.course_id,
            'registration_date': reg.registration_date.isoformat()
        })
    return jsonify({'registrations': output})