from app.helper.send_email import send_email_tool
from app.graphes.state import ClinicState
def send_conformation(state:ClinicState):
    
    email = state.get("email")
    appointment_time = state.get("appointment_time")

    if not email or not appointment_time:
        return {"status": "missing_info"}

    subject = "Appointment Confirmation"
    body = f"Your appointment is scheduled for {appointment_time}."

    if send_email_tool(email, subject, body):
        return {"appointment_status": "confirmed","confirmation_sent": True, "status": "confirmation_sent"}
    else:
        return {"appointment_status": "confirmation_failed","confirmation_sent": False, "status": "confirmation_failed"}