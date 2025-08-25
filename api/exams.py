from flask import request, jsonify
from . import api_blueprint
from models import db, Exams, Exam_Results, Courses, Students
from .auth import token_required, roles_required

# Yeni bir sınav oluşturma (Admin ve Professor)
@api_blueprint.route('/exams', methods=['POST'])
@roles_required(['Admin', 'Professor'])
def create_exam(current_user):
    data = request.get_json()
    exam_type = data.get('exam_type')
    exam_date = data.get('exam_date')
    course_id = data.get('course_id')

    if not all([exam_type, exam_date, course_id]):
        return jsonify({'error': 'Eksik bilgi.'}), 400
    
    course = Courses.query.get(course_id)
    if not course:
        return jsonify({'error': f'Course with id {course_id} not found'}), 404

    new_exam = Exams(
        exam_type=exam_type,
        exam_date=exam_date,
        course_id=course_id
    )
    
    try:
        db.session.add(new_exam)
        db.session.commit()
        return jsonify({'message': 'Sınav başarıyla oluşturuldu.', 'exam_id': new_exam.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Bir sınav için not girme (Admin ve Professor)
@api_blueprint.route('/exam_results', methods=['POST'])
@roles_required(['Admin', 'Professor'])
def add_exam_result(current_user):
    data = request.get_json()
    student_id = data.get('student_id')
    exam_id = data.get('exam_id')
    grade = data.get('grade')
    
    if not all([student_id, exam_id, grade]):
        return jsonify({'error': 'Eksik bilgilerden dolayı kayıt oluşturulamadı.'}), 400

    student = Students.query.get(student_id)
    exam = Exams.query.get(exam_id)
    if not student:
        return jsonify({'error': f'{student_id} numaralı öğrenci bulunamadı.'}), 404
    if not exam:
        return jsonify({'error': f'{exam_id} numaralı sınav bulunamadı.'}), 404

    existing_result = Exam_Results.query.filter_by(student_id=student_id, exam_id=exam_id).first()
    if existing_result:
        return jsonify({'message': 'Bu öğrenci ve sınav için sonuç zaten mevcut'}), 409

    new_result = Exam_Results(
        student_id=student_id,
        exam_id=exam_id,
        grade=grade
    )

    try:
        db.session.add(new_result)
        db.session.commit()
        return jsonify({'message': 'Sınav sonucu baraşıyla kaydedildi.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Bir öğrencinin tüm sınav sonuçlarını getirme (Admin, Professor ve Öğrenci)
@api_blueprint.route('/exam_results/student/<int:student_id>', methods=['GET'])
@token_required
def get_student_results(current_user, student_id):
    if current_user.role.role_name == 'Student' and student_id != current_user.student.id:
        return jsonify({'message': 'Erişim Reddedildi: Sadece kendi sınav sonuçlarınızı görebilirsiniz.'}), 403

    results = Exam_Results.query.filter_by(student_id=student_id).all()
    if not results:
        return jsonify({'message': 'Bu öğrenci için sınav sonucu bulunamadı.'}), 404

    output = []
    for result in results:
        output.append({
            'exam_id': result.exam_id,
            'grade': result.grade
        })
    return jsonify({'exam_results': output})