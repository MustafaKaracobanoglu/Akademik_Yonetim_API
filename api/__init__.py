from flask import Blueprint

api_blueprint = Blueprint('api', __name__)

from . import users, departments, courses, students, professors, registrations, exams, announcements, seed_data, auth