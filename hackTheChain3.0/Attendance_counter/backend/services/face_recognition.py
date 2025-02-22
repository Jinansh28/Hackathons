import face_recognition
from models.student import Student
from models.attendance import Attendance
from app import db
from datetime import date

def process_attendance(image_path):
    # Load the image
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)

    students = Student.query.all()
    marked_students = []

    for encoding in face_encodings:
        for student in students:
            match = face_recognition.compare_faces([student.face_encoding], encoding)
            if match[0]:
                marked_students.append(student.id)
                record_attendance(student.id, 'Present')
    
    # Mark absent for unrecognized students
    all_student_ids = [s.id for s in students]
    absent_students = list(set(all_student_ids) - set(marked_students))
    for student_id in absent_students:
        record_attendance(student_id, 'Absent')

    return {'present': marked_students, 'absent': absent_students}

def record_attendance(student_id, status):
    today = date.today()
    existing_record = Attendance.query.filter_by(student_id=student_id, date=today).first()

    if not existing_record:
        new_record = Attendance(student_id=student_id, date=today, status=status)
        db.session.add(new_record)
        db.session.commit()
