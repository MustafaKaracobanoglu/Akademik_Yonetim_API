from flask import request, jsonify
from . import api_blueprint
from models import db, Departments
from .auth import token_required, roles_required

# Tüm bölümleri listeleme (Herkes)
@api_blueprint.route('/departments', methods=['GET'])
def get_all_departments():
    departments = Departments.query.all()
    output = []
    for department in departments:
        output.append({'id': department.id, 'department_name': department.department_name})
    return jsonify({'departments': output})

# Yeni bir bölüm oluşturma (Sadece Admin)
@api_blueprint.route('/departments', methods=['POST'])
@roles_required(['Admin'])
def create_department(current_user):
    data = request.get_json()
    department_name = data.get('department_name')
    if not department_name:
        return jsonify({'error': 'Bölüm ismi gerekli.'}), 400

    new_department = Departments(department_name=department_name)
    try:
        db.session.add(new_department)
        db.session.commit()
        return jsonify({'message': 'Bölüm başarıyla oluşturuldu.', 'department_id': new_department.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Bölüm silme (Sadece Admin)
@api_blueprint.route('/departments/<int:department_id>', methods=['DELETE'])
@roles_required(['Admin'])
def delete_department(current_user, department_id):
    department = Departments.query.get_or_404(department_id)
    try:
        db.session.delete(department)
        db.session.commit()
        return jsonify({'message': 'Bölüm başarıyla silindi.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500