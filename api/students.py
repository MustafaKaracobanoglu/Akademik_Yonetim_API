from flask import request, jsonify
from . import api_blueprint
from models import db, Users, Students, Roles
from .auth import token_required, roles_required

# Yeni bir öğrenci ve kullanıcı hesabı oluşturma (Sadece Admin)
@api_blueprint.route('/students', methods=['POST'])
@roles_required(['Admin'])
def create_student(current_user):
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    student_id = data.get('student_id')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    department_id = data.get('department_id')

    if not all([username, password, email, student_id, first_name, last_name, department_id]):
        return jsonify({'error': 'Gerekli veriler eksik'}), 400

    student_role = Roles.query.filter_by(role_name='Student').first()
    if not student_role:
        return jsonify({'error': 'Öğrenci rolü bulunamadı'}), 500

    new_user = Users(
        username=username,
        password=password,
        email=email,
        role_id=student_role.id
    )

    try:
        db.session.add(new_user)
        db.session.flush()
        
        new_student = Students(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            user_id=new_user.id,
            department_id=department_id
        )
        db.session.add(new_student)
        db.session.commit()
        
        return jsonify({
            'message': 'Öğrenci ve kullanıcı hesabı başarıyla oluşturuldu',
            'user_id': new_user.id,
            'student_id': new_student.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Tüm öğrencileri listeleme (Sadece Admin ve Professor)
@api_blueprint.route('/students', methods=['GET'])
@roles_required(['Admin', 'Professor'])
def get_all_students(current_user):
    students = Students.query.all()
    output = []
    for student in students:
        output.append({
            'id': student.id,
            'student_id': student.student_id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'user_id': student.user_id,
            'department_id': student.department_id
        })
    return jsonify({'students': output})

# Belirli bir öğrenciyi ID ile getirme (Herkes, kendi bilgisine erişir)
@api_blueprint.route('/students/<int:student_id>', methods=['GET'])
@token_required
def get_student(current_user, student_id):
    student = Students.query.get_or_404(student_id)
    if current_user.role.role_name == 'Student' and student.user_id != current_user.id:
        return jsonify({'message': 'Erişim Reddedildi: Yalnızca kendi öğrenci bilgilerinizi görüntüleyebilirsiniz'}), 403
    
    return jsonify({
        'id': student.id,
        'student_id': student.student_id,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'user_id': student.user_id,
        'department_id': student.department_id
    })

# Öğrenci silme (Sadece Admin)
@api_blueprint.route('/students/<int:student_id>', methods=['DELETE'])
@roles_required(['Admin'])
def delete_student(current_user, student_id):
    student = Students.query.get_or_404(student_id)
    user_id = student.user_id
    try:
        db.session.delete(student)
        user = Users.query.get(user_id)
        if user:
            db.session.delete(user)
        
        db.session.commit()
        return jsonify({'message': 'Öğrenci ve ilgili kullanıcı hesabı başarıyla silindi'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500