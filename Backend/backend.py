from flask import Flask, render_template, request, jsonify
import cv2
import time
import pandas as pd
import numpy as np
import os
from datetime import datetime
import threading

# Initialize Flask app
app = Flask(__name__)

# Load OpenCV pre-trained face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Create face recognizer
face_recognizer = cv2.face.LBPHFaceRecognizer_create()

# Define directories
SNAPSHOT_DIR = "snapshots"
TRAINING_DIR = "training_faces"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)
os.makedirs(TRAINING_DIR, exist_ok=True)

# Define CSV files for attendance
ATTENDANCE_FILE = "attendance.csv"
ATTENDANCE_HISTORY_FILE = "attendance_history.csv"

# Dictionary to track student presence
student_presence = {}

# Timetable (as per your example)
timetable = {
    "Monday": {
        "Period 1": "Mr. Smith",
        "Period 2": "Dr. Brown",
        "Period 3": "Ms. Lee",
        "Period 4": "Ms. Davis",
        "Period 5": "Dr. Brown"
    },
    "Tuesday": {
        "Period 1": "Dr. Brown",
        "Period 2": "Mr. Smith",
        "Period 3": "Ms. Davis",
        "Period 4": "Ms. Lee",
        "Period 5": "Mr. Smith"
    },
    "Wednesday": {
        "Period 1": "Mr. Smith",
        "Period 2": "Ms. Davis",
        "Period 3": "Dr. Brown",
        "Period 4": "Ms. Lee",
        "Period 5": "Ms. Davis"
    },
    "Saturday": {
        "Period 1": "Ms. Lee",
        "Period 2": "Dr. Brown",
        "Period 3": "Mr. Smith",
        "Period 4": "Ms. Davis",
        "Period 5": "Ms. Lee"
    },
    "Sunday": {
        "Period 1": "Ms. Davis",
        "Period 2": "Ms. Lee",
        "Period 3": "Dr. Brown",
        "Period 4": "Mr. Smith",
        "Period 5": "Dr. Brown"
    }
}

# Period timings (adjust as needed)
period_timings = {
    "Period 1": "21:00-22:00",
    "Period 2": "22:00-23:00",
    "Period 3": "23:00-24:00",
    "Period 4": "00:00-01:00",
    "Period 5": "01:00-02:00"
}

# Global variable to track the last period for which attendance was marked
last_period = None

def capture_training_faces(student_name, num_images=20):
    """Capture and store training images for a student."""
    student_dir = os.path.join(TRAINING_DIR, student_name)
    os.makedirs(student_dir, exist_ok=True)
    cap = cv2.VideoCapture(0)
    count = 0

    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (200, 200))
            face_path = os.path.join(student_dir, f"face_{count}.jpg")
            cv2.imwrite(face_path, face)
            count += 1
            print(f"Saved {face_path}")

        cv2.imshow("Capturing Faces", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def train_face_recognizer():
    """Train the face recognizer using stored face images."""
    faces = []
    labels = []
    label_dict = {}
    label_id = 0

    for person in os.listdir(TRAINING_DIR):
        person_path = os.path.join(TRAINING_DIR, person)
        if os.path.isdir(person_path):
            label_dict[label_id] = person
            for img_name in os.listdir(person_path):
                img_path = os.path.join(person_path, img_name)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                faces.append(img)
                labels.append(label_id)
            label_id += 1

    if len(faces) > 0:
        face_recognizer.train(faces, np.array(labels))
        print("Face recognizer trained successfully!")
    else:
        print("No training data found. Please add training images first.")

    return label_dict

def capture_snapshots():
    """Capture 5 snapshots at 10-second intervals."""
    camera = cv2.VideoCapture(0)
    snapshots = []

    for i in range(5):
        time.sleep(2)
        ret, frame = camera.read()
        if not ret:
            print("Failed to capture image")
            continue

        filename = os.path.join(SNAPSHOT_DIR, f'snapshot_{i+1}.jpg')
        cv2.imwrite(filename, frame)
        snapshots.append(filename)
        print(f"Captured {filename}")

    camera.release()
    process_snapshots(snapshots)

def process_snapshots(snapshots):
    """Process snapshots and mark attendance."""
    global student_presence

    if not os.listdir(TRAINING_DIR):
        print("No training data available. Please train the model first.")
        return

    label_dict = train_face_recognizer()

    for snapshot in snapshots:
        frame = cv2.imread(snapshot)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (200, 200))

            try:
                label, confidence = face_recognizer.predict(face)
                student_id = label_dict.get(label, "Unknown") if confidence < 100 else "Unknown"
                student_presence[student_id] = student_presence.get(student_id, 0) + 1
            except cv2.error:
                print("Face recognizer model is not trained yet. Please train it first.")
                return

    mark_attendance()

def mark_attendance():
    """Mark attendance and update the permanent CSV file."""
    # Get the current date
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Prepare new attendance data
    all_students = [student for student in os.listdir(TRAINING_DIR)]
    data = []
    for student in all_students:
        status = "Present" if student_presence.get(student, 0) >= 3 else "Absent"
        data.append([current_date, student, status])

    # Create a DataFrame for the new attendance records
    df_new = pd.DataFrame(data, columns=["Date", "Student ID", "Status"])

    # Append the new records to the history file with error handling
    try:
        if os.path.exists(ATTENDANCE_HISTORY_FILE):
            df_history = pd.read_csv(ATTENDANCE_HISTORY_FILE)
        else:
            df_history = pd.DataFrame(columns=["Date", "Student ID", "Status"])
    except pd.errors.EmptyDataError:
        print("Attendance history file is empty. Initializing new DataFrame.")
        df_history = pd.DataFrame(columns=["Date", "Student ID", "Status"])
    except Exception as e:
        print(f"An error occurred while reading the history file: {e}")
        return

    df_combined = pd.concat([df_history, df_new], ignore_index=True)

    # Save the updated history file
    df_combined.to_csv(ATTENDANCE_HISTORY_FILE, index=False)
    print(f"Attendance history updated in {ATTENDANCE_HISTORY_FILE}")

    # Save the current attendance to the temporary file
    df_new.to_csv(ATTENDANCE_FILE, index=False)
    print(f"Current attendance saved in {ATTENDANCE_FILE}")

def send_attendance_to_teacher(teacher_name):
    """Send attendance data to the respective teacher by saving it in a file named after the teacher."""
    if os.path.exists(ATTENDANCE_FILE):
        df = pd.read_csv(ATTENDANCE_FILE)

        # Check if attendance DataFrame is empty
        if df.empty:
            print("Attendance file is empty. No data to send.")
            return

        # Sanitize teacher name for file naming
        safe_teacher_name = teacher_name.replace(" ", "_").lower()
        teacher_file = f"{safe_teacher_name}.csv"

        try:
            # Create teacher file if it doesn't exist
            if not os.path.exists(teacher_file):
                print(f"Creating new file for {teacher_name}: {teacher_file}")
                df.to_csv(teacher_file, index=False)
            else:
                # Append data if file exists
                df_teacher = pd.read_csv(teacher_file)
                df_combined = pd.concat([df_teacher, df], ignore_index=True)
                df_combined.to_csv(teacher_file, index=False)

            print(f"Attendance data saved for {teacher_name} in {teacher_file}")

        except Exception as e:
            print(f"Error saving file {teacher_file}: {e}")
    else:
        print(f"No attendance data found in {ATTENDANCE_FILE}.")

def timetable_monitor():
    """Monitor the timetable and send attendance data to the respective teacher."""
    global last_period  # Track the last period for which attendance was marked

    while True:
        now = datetime.now()
        current_day = now.strftime("%A")
        current_time = now.strftime("%H:%M")

        # Find the current period based on time
        current_period = None
        for period, timing in period_timings.items():
            start_time, end_time = timing.split("-")
            if start_time <= current_time <= end_time:
                current_period = period
                break

        # If a period is active and it's not the same as the last period
        if current_period and current_period != last_period:
            teacher_name = timetable[current_day][current_period]
            capture_snapshots()  # Capture snapshots and mark attendance
            send_attendance_to_teacher(teacher_name)
            last_period = current_period  # Update the last period
        elif not current_period:
            last_period = None  # Reset last_period if no period is active

        # Wait for 1 minute before checking again
        time.sleep(60)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture_training_faces')
def capture_training_faces_route():
    student_name = request.args.get('student_name')
    if not student_name:
        return "Student name is required.", 400
    capture_training_faces(student_name)
    return f"Training faces captured for {student_name}."

@app.route('/capture_snapshots')
def capture_snapshots_route():
    capture_snapshots()
    return "Snapshots captured and attendance marked."

if __name__ == '__main__':
    if os.listdir(TRAINING_DIR):
        train_face_recognizer()
    else:
        print("No training data available. Please add training images first.")

    # Start the timetable monitor in a separate thread
    timetable_thread = threading.Thread(target=timetable_monitor)
    timetable_thread.daemon = True
    timetable_thread.start()

    app.run(debug=False)