from app.helper.send_email import send_email_tool
from app.db.models import Appointment
from app.graphes.state import ClinicState
from app.db.db_config import SessionLocal


def send_reminder(state: ClinicState):

    email = state.get("email")
    appointment_time = state.get("appointment_time")
    patient_name = state.get("patient_name")
    appointment_id = state.get("appointment_id")

    if not email or not appointment_time or not patient_name:
        return {"status": "missing_info", "reminder_sent": False}

    subject = "Appointment Reminder"

    body = f"""
Hello {patient_name},

This is a reminder that you have a doctor appointment scheduled at:

{appointment_time}

Please arrive 10 minutes early.

Best regards,
Clinic Team
"""

    email_sent = send_email_tool(email, subject, body)

    if not email_sent:
        return {"status": "reminder_failed", "reminder_sent": False}

    if appointment_id:
        db = SessionLocal()
        try:
            appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()

            if appt:
                appt.reminder_sent = True
                db.commit()

        finally:
            db.close()

    print(f"Reminder sent to {email}")

    return {"reminder_sent": True, "status": "reminder_sent"}