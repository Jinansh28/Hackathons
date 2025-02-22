from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db = SQLAlchemy(app)

# Import and register routes
from routes.students import students_bp
from routes.attendance import attendance_bp

app.register_blueprint(students_bp, url_prefix='/api/students')
app.register_blueprint(attendance_bp, url_prefix='/api/attendance')

if __name__ == '__main__':
    app.run(debug=True)
