from flask import Blueprint, request, jsonify
from models.attendance import Attendance
from services.face_recognition import process_attendance
from app import db

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/', methods=['POST'])
def mark_attendance():
    data = request.json
    image_path = data.get('image_path')

    if not image_path:
        return jsonify({'error': 'Image path is required'}), 400

    attendance_result = process_attendance(image_path)
    return jsonify({'message': 'Attendance processed', 'result': attendance_result}), 200
