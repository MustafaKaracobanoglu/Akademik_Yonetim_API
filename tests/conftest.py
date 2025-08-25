import pytest
from app import app as flask_app, db as flask_db
from models import Users, Roles

@pytest.fixture(scope='session')
def app():
    """Tüm testler için bir uygulama bağlamı oluşturur."""
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with flask_app.app_context():
        # Test için gerekli tabloları oluştur
        flask_db.create_all()
        yield flask_app
        # Testler bittikten sonra tabloları temizle
        flask_db.drop_all()

@pytest.fixture(scope='function')
def test_client(app):
    """API testleri için bir test istemcisi sağlar."""
    return app.test_client()

@pytest.fixture(scope='function')
def db(app):
    """Her test için izole edilmiş bir veritabanı oturumu sağlar."""
    with app.app_context():
        flask_db.session.begin_nested()
        yield flask_db
        flask_db.session.rollback()

@pytest.fixture(scope='function')
def admin_user(app, db):
    """Bir Admin kullanıcısı oluşturup veritabanına ekler."""
    with app.app_context():
        role = Roles.query.filter_by(role_name='Admin').first()
        if not role:
            role = Roles(role_name='Admin')
            db.session.add(role)
            db.session.commit()

        user = Users(username='admin_test', email='admin@test.com', role=role)
        user.password = 'password123'
        db.session.add(user)
        db.session.commit()

        return db.session.get(Users, user.id)

@pytest.fixture(scope='function')
def student_user(app, db):
    """Bir Student kullanıcısı oluşturup veritabanına ekler."""
    with app.app_context():
        role = Roles.query.filter_by(role_name='Student').first()
        if not role:
            role = Roles(role_name='Student')
            db.session.add(role)
            db.session.commit()

        user = Users(username='student_test', email='student@test.com', role=role)
        user.password = 'password123'
        db.session.add(user)
        db.session.commit()

        return db.session.get(Users, user.id)

@pytest.fixture(scope='function')
def admin_token(test_client, admin_user):
    """Admin kullanıcısı için bir JWT token'ı sağlar."""
    response = test_client.post(
        '/api/login',
        json={
            'username': admin_user.username,
            'password': 'password123'
        }
    )
    return response.json['token']

@pytest.fixture(scope='function')
def student_token(test_client, student_user):
    """Student kullanıcısı için bir JWT token'ı sağlar."""
    response = test_client.post(
        '/api/login',
        json={
            'username': student_user.username,
            'password': 'password123'
        }
    )
    return response.json['token']