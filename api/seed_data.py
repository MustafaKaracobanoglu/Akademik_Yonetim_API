from flask import jsonify
from . import api_blueprint
from models import db, Roles, Departments, Users, Students, Professors, Courses, Exams, Announcements, Course_Registrations, Exam_Results
import datetime

@api_blueprint.route('/seed_data', methods=['POST'])
def seed_data():
    """Create essential data for all tables to prevent foreign key errors."""
    try:
        # Check if data already exists to prevent duplicates
        if Departments.query.first() and Users.query.first():
            return jsonify({'message': 'Initial data already exists. No new data added.'}), 200

        # Create a Department
        department = Departments(department_name='Bilgisayar Mühendisliği')
        db.session.add(department)
        db.session.flush()

        # Create Roles if they don't exist
        admin_role = Roles.query.filter_by(role_name='Admin').first()
        if not admin_role:
            return jsonify({'error': 'Admin role not found. Please run "flask seed_roles" first.'}), 500

        professor_role = Roles.query.filter_by(role_name='Professor').first()
        student_role = Roles.query.filter_by(role_name='Student').first()

        # Create a Professor and a User account for the professor
        professor_user = Users(
            username='prof.demir',
            password='123',
            email='prof.demir@example.com',
            role_id=professor_role.id
        )
        db.session.add(professor_user)
        db.session.flush()

        professor = Professors(
            first_name='Ahmet',
            last_name='Demir',
            title='Dr.',
            user_id=professor_user.id,
            department_id=department.id
        )
        db.session.add(professor)
        
        # Create a Student and a User account for the student
        student_user = Users(
            username='ayse.yilmaz',
            password='123',
            email='ayse.yilmaz@example.com',
            role_id=student_role.id
        )
        db.session.add(student_user)
        db.session.flush()

        student = Students(
            student_id='2024001',
            first_name='Ayşe',
            last_name='Yılmaz',
            user_id=student_user.id,
            department_id=department.id
        )
        db.session.add(student)

        # Create a Course linked to the department and professor
        course = Courses(
            course_code='CS101',
            course_name='Programlamaya Giriş',
            credits=3,
            department_id=department.id,
            professor_id=professor.id
        )
        db.session.add(course)
        db.session.flush()
        
        # Create a Course Registration for the student and course
        registration = Course_Registrations(
            student_id=student.id,
            course_id=course.id
        )
        db.session.add(registration)

        # Create an Exam for the course
        exam = Exams(
            exam_type='Vize',
            exam_date=datetime.datetime.now(),
            course_id=course.id
        )
        db.session.add(exam)
        db.session.flush()

        # Create an Exam Result for the student and exam
        exam_result = Exam_Results(
            student_id=student.id,
            exam_id=exam.id,
            grade=85.5
        )
        db.session.add(exam_result)

        # Create an Announcement for the course
        announcement = Announcements(
            title='Ders Notu',
            content='Yeni ders notu sisteme yüklendi.',
            course_id=course.id
        )
        db.session.add(announcement)
        
        db.session.commit()

        return jsonify({'message': 'All essential data created successfully.'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500