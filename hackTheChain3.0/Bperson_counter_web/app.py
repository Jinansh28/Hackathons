from flask import Flask, render_template, Response
import cv2
from ultralytics import YOLO

# Initialize Flask app
app = Flask(__name__)

# Initialize webcam
camera = cv2.VideoCapture(0)

# Load YOLOv8 pre-trained model
model = YOLO('yolov8n.pt')  # Use 'yolov8n.pt' (nano) for speed or 'yolov8s.pt' (small) for better accuracy

def generate_frames():
    while True:
        # Read frame from webcam
        success, frame = camera.read()
        if not success:
            break
        else:
            # Resize frame for performance
            frame_resized = cv2.resize(frame, (640, 480))

            # Run YOLOv8 detection
            results = model(frame_resized)

            # Filter detections for 'person' class (class ID 0 in COCO dataset)
            person_count = 0
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    if cls_id == 0:  # Class 0 is 'person' in YOLO's COCO model
                        person_count += 1
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cv2.rectangle(frame_resized, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame_resized, "Person", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Display person count
            cv2.putText(frame_resized, f'Count: {person_count}', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame_resized)
            frame = buffer.tobytes()

            # Yield frame for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route for video feed
@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
