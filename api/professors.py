from flask import request, jsonify
from . import api_blueprint
from models import db, Users, Professors, Roles
from .auth import token_required, roles_required

# Yeni bir akademisyen ve kullanıcı hesabı oluşturma (Sadece Admin)
@api_blueprint.route('/professors', methods=['POST'])
@roles_required(['Admin'])
def create_professor(current_user):
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    title = data.get('title')
    department_id = data.get('department_id')

    if not all([username, password, email, first_name, last_name, department_id]):
        return jsonify({'error': 'Eksik bilgi girildi.'}), 400

    professor_role = Roles.query.filter_by(role_name='Professor').first()
    if not professor_role:
        return jsonify({'error': 'Profesör rölü bulunamadı.'}), 500
    
    new_user = Users(
        username=username,
        password=password,
        email=email,
        role_id=professor_role.id
    )

    try:
        db.session.add(new_user)
        db.session.flush()
        
        new_professor = Professors(
            first_name=first_name,
            last_name=last_name,
            title=title,
            user_id=new_user.id,
            department_id=department_id
        )
        db.session.add(new_professor)
        db.session.commit()
        
        return jsonify({
            'message': 'Profesör ve kullanıcı hesabı başarıyla oluşturuldu',
            'user_id': new_user.id,
            'professor_id': new_professor.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Tüm akademisyenleri listeleme (Herkes)
@api_blueprint.route('/professors', methods=['GET'])
def get_all_professors():
    professors = Professors.query.all()
    output = []
    for professor in professors:
        output.append({
            'id': professor.id,
            'first_name': professor.first_name,
            'last_name': professor.last_name,
            'title': professor.title,
            'user_id': professor.user_id,
            'department_id': professor.department_id
        })
    return jsonify({'professors': output})

# Belirli bir akademisyeni ID ile getirme (Herkes, kendi bilgisine erişir)
@api_blueprint.route('/professors/<int:professor_id>', methods=['GET'])
@token_required
def get_professor(current_user, professor_id):
    professor = Professors.query.get_or_404(professor_id)
    if current_user.role.role_name == 'Professor' and professor.user_id != current_user.id:
        return jsonify({'message': 'Erişim Reddedildi: Yalnızca kendi profesör bilgilerinizi görüntüleyebilirsiniz'}), 403
    
    return jsonify({
        'id': professor.id,
        'first_name': professor.first_name,
        'last_name': professor.last_name,
        'title': professor.title,
        'user_id': professor.user_id,
        'department_id': professor.department_id
    })

# Akademisyen silme (Sadece Admin)
@api_blueprint.route('/professors/<int:professor_id>', methods=['DELETE'])
@roles_required(['Admin'])
def delete_professor(current_user, professor_id):
    professor = Professors.query.get_or_404(professor_id)
    user_id = professor.user_id
    try:
        db.session.delete(professor)
        user = Users.query.get(user_id)
        if user:
            db.session.delete(user)
        
        db.session.commit()
        return jsonify({'message': 'Profesör ve ilgili kullanıcı hesabı başarıyla silindi.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500