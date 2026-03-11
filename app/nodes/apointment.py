from app.db.models import Appointment
from app.db.db_config import SessionLocal
from app.graphes.state import ClinicState
def schedule_appointment(state: ClinicState):

    db = SessionLocal()

    appointment = Appointment(
        patient_id=state["patient_id"],
        appointment_time=state.get("appointment_time")
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    db.close()

    return {
        "appointment_id": appointment.id,
        "appointment_time": appointment.appointment_time,
        "appointment_status": "scheduled",
        "status": "appointment_scheduled"
    }