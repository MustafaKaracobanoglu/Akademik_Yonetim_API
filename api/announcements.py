from flask import request, jsonify
from . import api_blueprint
from models import db, Announcements, Courses
from .auth import token_required, roles_required

# Yeni bir duyuru oluşturma (Admin ve Professor)
@api_blueprint.route('/announcements', methods=['POST'])
@roles_required(['Admin', 'Professor'])
def create_announcement(current_user):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    course_id = data.get('course_id')

    if not all([title, content]):
        return jsonify({'error': 'Eksik bilgiden dolayı kayıt oluşturalamadı!'}), 400
    
    if course_id:
        course = Courses.query.get(course_id)
        if not course:
            return jsonify({'error': f'{course_id} numaralı ders bulunamadı.'}), 404

    new_announcement = Announcements(
        title=title,
        content=content,
        course_id=course_id
    )

    try:
        db.session.add(new_announcement)
        db.session.commit()
        return jsonify({'message': 'Duyuru başarıyla oluşturuldu.', 'announcement_id': new_announcement.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Tüm duyuruları listeleme (Herkes)
@api_blueprint.route('/announcements', methods=['GET'])
def get_all_announcements():
    announcements = Announcements.query.all()
    output = []
    for ann in announcements:
        output.append({
            'id': ann.id,
            'title': ann.title,
            'content': ann.content,
            'date_posted': ann.date_posted.isoformat(),
            'course_id': ann.course_id
        })
    return jsonify({'announcements': output})