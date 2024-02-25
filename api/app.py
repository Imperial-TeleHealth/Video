from flask import Flask, request, jsonify, render_template, abort
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///video-test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Appointment(db.Model):
    id = db.Column(db.String, primary_key=True)
    patient_id = db.Column(db.String(80), nullable=False)
    doctor_id = db.Column(db.String(80), nullable=False)
    schedule_time = db.Column(db.String(80), nullable=False)
    meeting_link = db.Column(db.String(256), nullable=False)

with app.app_context():
    db.create_all()

@app.route("/")
def root():
    return jsonify({"message": "Hello World"})

def create_jitsi_meeting(patient_id, doctor_id, schedule_time):
    meeting_link = f"https://meet.jit.si/{patient_id}+{doctor_id}+{schedule_time}"
    return meeting_link

def store_appointment(patient_id, doctor_id, schedule_time, meeting_link):
    appointment_id = str(uuid.uuid4()) 
    new_appointment = Appointment(id=appointment_id, patient_id=patient_id, doctor_id=doctor_id, schedule_time=schedule_time, meeting_link=meeting_link)
    db.session.add(new_appointment)
    db.session.commit()
    return appointment_id
        
# Want to schedule appointment
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



if __name__ == '__main__':
    app.run(debug=True)
