from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

# Models must be defined in an order that respects foreign key dependencies.
# For example, a table that references another should be defined after the referenced table.

class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('Users', backref='role', lazy=True)
    def __repr__(self):
        return f'<Role {self.role_name}>'

class Departments(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(100), unique=True, nullable=False)
    courses = db.relationship('Courses', backref='department', lazy=True)
    professors = db.relationship('Professors', backref='department', lazy=True)
    students = db.relationship('Students', backref='department', lazy=True)
    def __repr__(self):
        return f'<Department {self.department_name}>'

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    _password = db.Column(db.String(255), nullable=False) # Parolanın şifrelenmiş hali
    email = db.Column(db.String(120), unique=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    student = db.relationship('Students', backref='user', uselist=False)
    professor = db.relationship('Professors', backref='user', uselist=False)

    @property
    def password(self):
        """Parolayı doğrudan okumayı engelle."""
        raise AttributeError('Parola okunamıyor.')

    @password.setter
    def password(self, password_text):
        """Parolayı şifreleyerek _password alanına yazar."""
        self._password = bcrypt.generate_password_hash(password_text).decode('utf-8')

    def check_password(self, password_text):
        """Girilen parolayı şifrelenmiş parola ile karşılaştırır."""
        return bcrypt.check_password_hash(self._password, password_text)

    def __repr__(self):
        return f'<User {self.username}>'

class Students(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    course_registrations = db.relationship('Course_Registrations', backref='student', lazy=True)
    exam_results = db.relationship('Exam_Results', backref='student', lazy=True)
    def __repr__(self):
        return f'<Student {self.student_id}>'

class Professors(db.Model):
    __tablename__ = 'professors'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    courses = db.relationship('Courses', backref='professor', lazy=True)
    def __repr__(self):
        return f'<Professor {self.first_name} {self.last_name}>'

class Courses(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=True)
    course_registrations = db.relationship('Course_Registrations', backref='course', lazy=True)
    exams = db.relationship('Exams', backref='course', lazy=True)
    announcements = db.relationship('Announcements', backref='course', lazy=True)
    def __repr__(self):
        return f'<Course {self.course_code}>'

class Course_Registrations(db.Model):
    __tablename__ = 'course_registrations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=db.func.now())
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='_student_course_uc'),)
    def __repr__(self):
        return f'<Course Registration student_id:{self.student_id} for course_id:{self.course_id}>'

class Exams(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    exam_type = db.Column(db.String(50), nullable=False)
    exam_date = db.Column(db.DateTime, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    exam_results = db.relationship('Exam_Results', backref='exam', lazy=True)
    def __repr__(self):
        return f'<Exam {self.exam_type} for Course {self.course_id}>'

class Exam_Results(db.Model):
    __tablename__ = 'exam_results'
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Float, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('student_id', 'exam_id', name='_student_exam_uc'),)
    def __repr__(self):
        return f'<Exam Result for student_id:{self.student_id} and exam_id:{self.exam_id}>'

class Announcements(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=db.func.now())
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    def __repr__(self):
        return f'<Announcement {self.title}>'