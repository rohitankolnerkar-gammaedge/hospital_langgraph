from app.helper.send_email import send_email_tool
from app.db.models import Appointment
from app.graphes.state import ClinicState
from app.db.db_config import SessionLocal
from fastapi import HTTPException
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
async def send_reminder(email,appointment_time,patient_name,appointment_id):

    email = email
    appointment_time = appointment_time
    patient_name = patient_name
    appointment_id = appointment_id

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

    try:
        async with sse_client("http://localhost:8001/sse") as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                print(await session.list_tools())
                email_sent= await session.call_tool(
                    "send_email_tool",
                    {"to_email": email, "subject": subject,"body":body}
                )
                
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP session or PDF extraction failed: {e}")

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