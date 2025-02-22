import pandas as pd
from models.attendance import Attendance
from models.student import Student
from app import db

def export_attendance_to_excel():
    records = db.session.query(Attendance, Student).join(Student, Attendance.student_id == Student.id).all()

    data = []
    for attendance, student in records:
        data.append({
            'Date': attendance.date,
            'Student Name': student.name,
            'Roll Number': student.roll_number,
            'Status': attendance.status
        })

    df = pd.DataFrame(data)
    df.to_excel('attendance_report.xlsx', index=False)
    print("Attendance exported to attendance_report.xlsx")
