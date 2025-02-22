

from flask import Flask, render_template
import cv2
import time
import pandas as pd
import numpy as np
import os

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

# Define CSV file for attendance
ATTENDANCE_FILE = "attendance.csv"

# Dictionary to track student presence
student_presence = {}

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
        time.sleep(10)
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
    """Mark attendance if a student appears in at least 3 snapshots."""
    data = [[student, "Present" if count >= 3 else "Absent"] for student, count in student_presence.items()]
    df = pd.DataFrame(data, columns=["Student ID", "Status"])
    df.to_csv(ATTENDANCE_FILE, index=False)
    print("Attendance recorded in attendance.csv")

@app.route('/')
def index():
    return render_template('index.html', message="Attendance snapshots are being processed. Check attendance.csv for results.")

if __name__ == '__main__':
    if os.listdir(TRAINING_DIR):
        train_face_recognizer()
    else:
        print("No training data available. Please add training images first.")
    
    capture_snapshots()
    app.run(debug=True)
