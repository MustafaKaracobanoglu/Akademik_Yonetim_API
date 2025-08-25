from flask import request, jsonify
from . import api_blueprint
from models import db, Users, Roles # 'Roles' modelini import etmeyi unutma
from .auth import token_required, roles_required

# Tüm kullanıcıları getirme (Sadece Admin)
@api_blueprint.route('/users', methods=['GET'])
@roles_required(['Admin'])
def get_all_users(current_user):
    users = Users.query.all()
    output = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role_id': user.role_id
        }
        output.append(user_data)
    return jsonify({'users': output})

# Yeni kullanıcı oluşturma (Sadece Admin)
@api_blueprint.route('/users', methods=['POST'])
@roles_required(['Admin']) # Bu dekoratörü kullanarak sadece adminlerin kullanıcı oluşturmasını sağla
def create_user(current_user):
    # Bu kontrolü token_required yerine roles_required dekoratörü hallediyor.
    # if current_user.role.role_name != 'Admin':
    #     return jsonify({'message': 'Yalnızca yöneticiler yeni kullanıcı oluşturabilir.'}), 403

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role_id = data.get('role_id')

    # Boş alan kontrolü
    if not all([username, password, email, role_id]):
        return jsonify({'error': 'Missing data'}), 400
    
    # Kullanıcı adı veya e-posta zaten var mı kontrolü
    if Users.query.filter_by(username=username).first() or Users.query.filter_by(email=email).first():
        return jsonify({'error': 'Kullanıcı adı veya e-posta zaten kullanımda'}), 409
    
    # Role'ün varlığını kontrol et
    role = db.session.get(Roles, role_id)
    if not role:
        return jsonify({'error': 'Geçersiz rol belirtildi'}), 400

    new_user = Users(
        username=username,
        password=password, # @password.setter metodu bu satırda çalışır ve parolayı hashler
        email=email,
        role_id=role_id
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'message': 'User created successfully',
            'user_id': new_user.id,
            'username': new_user.username,
            'role_name': new_user.role.role_name
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Kullanıcı oluşturulurken bir hata oluştu: ' + str(e)}), 500

# Belirli bir kullanıcıyı ID ile getirme (Kullanıcı kendisi veya Admin)
@api_blueprint.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    if current_user.id != user_id and current_user.role.role_name != 'Admin':
        return jsonify({'message': 'Erişim Reddedildi: Yalnızca kendi profilinizi görüntüleyebilirsiniz veya yetkiniz yok'}), 403
    
    user = Users.query.get_or_404(user_id)
    if not user:
        return jsonify({'message': 'Kullanıcı bulunamadı'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role_id': user.role_id,
        'role_name': user.role.role_name # Rol adını da ekle
    })

# Kullanıcı güncelleme (Kullanıcı kendisi veya Admin)
@api_blueprint.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    if current_user.id != user_id and current_user.role.role_name != 'Admin':
        return jsonify({'message': 'Erişim Reddedildi: Yalnızca kendi profilinizi güncelleyebilirsiniz veya yetkiniz yok.'}), 403
    
    user = Users.query.get_or_404(user_id)
    data = request.get_json()

    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    if 'password' in data:
        user.password = data.get('password')

    try:
        db.session.commit()
        return jsonify({'message': 'Kullanıcı başarıyla güncellendi.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Kullanıcı güncellenirken bir hata oluştu: ' + str(e)}), 500

# Kullanıcı silme (Sadece Admin)
@api_blueprint.route('/users/<int:user_id>', methods=['DELETE'])
@roles_required(['Admin'])
def delete_user(current_user, user_id):
    user = Users.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Kullanıcı başarıyla silindi.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Kullanıcı silinirken bir hata oluştu: ' + str(e)}), 500