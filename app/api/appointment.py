from fastapi import APIRouter
from datetime import datetime
from app.db.db_config import SessionLocal
from app.db.models import DoctorSchedule

router = APIRouter()

@router.get("/appointments/{doctor_id}")
def patient_intake(doctor_id: int):

    db = SessionLocal()

    slots = db.query(DoctorSchedule).filter(
        DoctorSchedule.doctor_id == doctor_id,
        DoctorSchedule.is_booked == False,
        DoctorSchedule.slot_time > datetime.utcnow()
    ).all()

    db.close()

    available_slots = [
        {
            "slot_id": slot.id,
            "slot_time": slot.slot_time
        }
        for slot in slots
    ]

    return {
        "message": "Welcome to the clinic. Please choose an appointment slot.",
        "available_slots": available_slots
    }