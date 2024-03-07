from flask import Flask, request, jsonify, abort, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import text
import uuid
import urllib.parse
import os

# load_dotenv()

app = Flask(__name__)

password = os.getenv('AY_AZURE_SQL_PASSWORD')
username = os.getenv('AY_AZURE_SQL_USERNAME')

params = urllib.parse.quote_plus("DRIVER={ODBC Driver 18 for SQL Server};"
                                 "Server=tcp:telehealth-video.database.windows.net,1433;"
                                 "Database=video;"
                                 f"Uid={username};"
                                 f"Pwd={password};"
                                 "Encrypt=yes;"
                                 "TrustServerCertificate=no;"
                                 "Connection Timeout=30;")

app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route("/")
def home():
    return "Welcome to Telehealth Video API!"


@app.route("/test-db")
def test_db():
    try:
        # Directly execute a raw SQL command
        result = db.session.execute(text("SELECT 1")).fetchall()
        return 'Success!'
    except Exception as e:
        return str(e)

class Appointment(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    patient_id = db.Column(db.String(80), nullable=False)
    doctor_id = db.Column(db.String(80), nullable=False)
    schedule_time = db.Column(db.String(80), nullable=False)
    meeting_link = db.Column(db.String(256), nullable=False)

with app.app_context():
    db.create_all()

@app.route("/")
def root():
    return render_template('schedule-appointment.html')

# Create a Jitsi meeting link
def create_jitsi_meeting(patient_id, doctor_id, schedule_time):
    meeting_link = f"https://meet.jit.si/{patient_id}+{doctor_id}+{schedule_time}"
    return meeting_link

def store_appointment(patient_id, doctor_id, schedule_time, meeting_link):
    appointment_id = str(uuid.uuid4()) 
    new_appointment = Appointment(id=appointment_id, patient_id=patient_id, doctor_id=doctor_id, schedule_time=schedule_time, meeting_link=meeting_link)
    db.session.add(new_appointment)
    db.session.commit()
    return appointment_id

def retrieve_sample_data():
    data = db.session.query(Appointment).all()
    return data

# Create endpoint to retrieve sample data from the database
@app.route('/add-sample-data', methods=['GET', 'POST'])
def add_sample_data():
    if request.method == 'POST':
        data = request.get_json()
        appointment_id = store_appointment(data['patient_id'], data['doctor_id'], data['schedule_time'], data['meeting_link'])
        return jsonify({"appointment_id": appointment_id})
    else:
        data = retrieve_sample_data()  # function to retrieve sample data from the database
        return render_template('index.html', data=data)


# Want to schedule appointment 
# @app.route('/schedule-appointment', methods=['POST'])
# def schedule_appointment():
#     data = request.form
#     meeting_link = create_jitsi_meeting(data['patient_id'], data['doctor_id'], data['schedule_time'])
#     appointment_id = store_appointment(data['patient_id'], data['doctor_id'], data['schedule_time'], meeting_link)
#     return jsonify({"appointment_id": appointment_id, "meeting_link": meeting_link})


@app.route('/schedule-appointment', methods=['POST'])
def schedule_appointment():
    data = request.get_json()
    meeting_link = create_jitsi_meeting(data['patient_id'], data['doctor_id'], data['schedule_time'])
    appointment_id = store_appointment(data['patient_id'], data['doctor_id'], data['schedule_time'], meeting_link)
    return jsonify({"appointment_id": appointment_id, "meeting_link": meeting_link})

# Want to join a video call
@app.route('/join-video-call/<appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        abort(404, description="Appointment not found")
    return jsonify({"meeting_link": appointment.meeting_link})

# Want to delete appointment
@app.route('/delete-appointment/<appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        abort(404, description="Appointment not found")
    db.session.delete(appointment)
    db.session.commit()
    return jsonify({"message": "Appointment deleted"})

if __name__ == '__main__':
    app.run(debug=True)
