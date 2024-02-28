from flask_testing import TestCase
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'api')))

from flask import Flask, json
from app import app, db, Appointment

class TestVideoMicroService(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_apppointment_scheduling(self):
        payload = {
            "patient_id": "test_patient_id",
            "doctor_id": "test_doctor_id",
            "schedule_time": "2023-01-01T10:00:00"
        }
        response = self.client.post('/schedule-appointment', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('appointment_id', data)
        self.assertIn('meeting_link', data)
        self.assertTrue("meet.jit.si" in data['meeting_link'])
        self.assertNotEqual(data['appointment_id'], "")
        self.assertNotEqual(data['meeting_link'], "")

    def test_join_video_call(self):
        appointment = Appointment(id='some-unique-appointment-id', patient_id='1', doctor_id='1', schedule_time='10:00', meeting_link='https://meet.jit.si/1+1+10:00')
        db.session.add(appointment)
        db.session.commit()

        response = self.client.get(f'/join-video-call/some-unique-appointment-id')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('meeting_link', data)
        self.assertTrue("meet.jit.si" in data['meeting_link'])
        self.assertNotEqual(data['meeting_link'], "")

    def test_delete_appointment(self):
        appointment = Appointment(id='some-unique-appointment-id', patient_id='1', doctor_id='1', schedule_time='10:00', meeting_link='https://meet.jit.si/1+1+10:00')
        db.session.add(appointment)
        db.session.commit()

        response = self.client.delete(f'/delete-appointment/some-unique-appointment-id')
        self.assertEqual(db.session.get(Appointment, 'some-unique-appointment-id'), None)

