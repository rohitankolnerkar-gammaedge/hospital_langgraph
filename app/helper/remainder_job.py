from app.db.db_config import SessionLocal
from app.db.models import Appointment, PatientRecord
from app.nodes.send_remainder import send_reminder


def reminder_job():

    print("Checking appointments for reminders...")

    db = SessionLocal()

    appointments = db.query(Appointment).filter(
        Appointment.status == "scheduled",
        Appointment.reminder_sent == False
    ).all()

    for appt in appointments:

        patient = db.query(PatientRecord).filter(
            PatientRecord.id == appt.patient_id
        ).first()

        if not patient:
            continue

        state = {
            "email": patient.email,
            "patient_name": patient.patient_name,
            "appointment_time": appt.appointment_time,
            "appointment_id": appt.id
        }

        send_reminder(state)

    db.close()