from flask import request, jsonify, current_app
from . import api_blueprint
from models import Users, db
import jwt
import datetime
from datetime import timezone
from functools import wraps

@api_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({'error': 'Eksik Kullanıcı Adı Veya Parola'}), 400

    user = Users.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Geçersiz Kullanıcı Adı Veya Parola '}), 401
    
    token_payload = {
        'id': user.id,
        'username': user.username,
        'role_id': user.role_id,
        'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=24)
    }

    token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'message': 'Giriş Başarılı', 'token': token}), 200

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = db.session.get(Users, data['id'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401
        except Exception as e:
            return jsonify({'message': str(e)}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def roles_required(roles):
    def wrapper(f):
        @wraps(f)
        @token_required
        def decorated_function(current_user, *args, **kwargs):
            if current_user.role.role_name not in roles:
                return jsonify({'message': 'Access forbidden: Erişim Engellendi'}), 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return wrapper

@api_blueprint.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    return jsonify({
        'message': f'Hello, {current_user.username}! Your ID is {current_user.id} and you have a role_id of {current_user.role_id}. This is a protected route.'
    })