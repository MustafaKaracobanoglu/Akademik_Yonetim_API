from flask import Flask, send_from_directory
from models import db, bcrypt, Roles, Departments, Users
from api import api_blueprint
from flask_swagger_ui import get_swaggerui_blueprint
import os
from flask_cors import CORS

# Flask uygulaması
app = Flask(__name__)
CORS(app)

# Veritabanı bağlantı ayarları
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:1234@db:5432/akademik_yonetim'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sifreleme_icin_cok_gizli_bir_anahtar'

# SQLAlchemy ve Bcrypt nesnelerini uygulamaya bağlama
db.init_app(app)
bcrypt.init_app(app)

# Ana API blueprint'ini uygulamaya kaydetme
app.register_blueprint(api_blueprint, url_prefix='/api')

# Swagger UI'ı ayarlama
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Akademik Yönetim Sistemi"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Swagger dosyasını sunma rotası
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def home():
    return 'Merhaba, Akademik Yönetim Sistemi! API dokümantasyonu için /api/docs adresini ziyaret edin.'

# Komut satırı araçları
@app.cli.command("seed_roles")
def seed_roles():
    """Add initial roles to the database."""
    with app.app_context():
        if Roles.query.first():
            print("Roller zaten mevcut, ekleme yapılmadı.")
            return
        roles_to_add = [
            Roles(role_name='Admin'), # type: ignore
            Roles(role_name='Professor'), # type: ignore
            Roles(role_name='Student') # type: ignore
        ]
        db.session.add_all(roles_to_add)
        db.session.commit()
        print("Başlangıç rolleri başarıyla eklendi.")

@app.cli.command("create_admin")
def create_admin():
    """Create an initial admin user."""
    with app.app_context():
        admin_role = Roles.query.filter_by(role_name='Admin').first()
        if not admin_role:
            print("Hata: 'Admin' rolü bulunamadı. Lütfen önce 'flask seed_roles' komutunu çalıştırın.")
            return
        
        if Users.query.filter_by(username='admin').first():
            print("Admin kullanıcısı zaten mevcut. Yeni kullanıcı oluşturulmadı.")
            return

        new_admin = Users(
            username='admin',
            password='123',
            email='admin@university.edu',
            role_id=admin_role.id
        )
        db.session.add(new_admin)
        db.session.commit()
        print("Admin kullanıcısı başarıyla oluşturuldu.")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Tüm veritabanı tabloları güncellendi.")
    app.run(host="0.0.0.0", port=5000)