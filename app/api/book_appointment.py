from fastapi import APIRouter, HTTPException
from app.db.db_config import SessionLocal
from app.db.models import DoctorSchedule, Appointment

router = APIRouter()

@router.post("/book-appointment")
def book_appointment(slot_id: int, patient_id: int):

    db = SessionLocal()

    slot = db.query(DoctorSchedule).filter(
        DoctorSchedule.id == slot_id,
        DoctorSchedule.is_booked == False
    ).first()

    if not slot:
        db.close()
        raise HTTPException(status_code=400, detail="Slot not available")

    appointment = Appointment(
        patient_id=patient_id,
        appointment_time=slot.slot_time,
        status="scheduled"
    )

    db.add(appointment)

    slot.is_booked = True

    db.commit()
    db.refresh(appointment)
    db.close()

    return {
        "message": "Appointment booked successfully",
        "appointment_id": appointment.id,
        "appointment_time": slot.slot_time
    }