from flask import Blueprint, request, jsonify
from models.student import Student
from app import db

students_bp = Blueprint('students', __name__)

@students_bp.route('/', methods=['POST'])
def add_student():
    data = request.json
    try:
        new_student = Student(
            name=data['name'],
            roll_number=data['roll_number'],
            face_encoding=data['face_encoding']
        )
        db.session.add(new_student)
        db.session.commit()
        return jsonify({'message': 'Student added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@students_bp.route('/', methods=['GET'])
def get_students():
    students = Student.query.all()
    output = [{'id': s.id, 'name': s.name, 'roll_number': s.roll_number} for s in students]
    return jsonify(output), 200
