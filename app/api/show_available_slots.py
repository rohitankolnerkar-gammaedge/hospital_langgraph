from fastapi import APIRouter
from app.db.db_config import SessionLocal
from app.db.models import Appointment,DoctorSchedule
from datetime import datetime, timedelta

show_slots = APIRouter(prefix="/api")

@show_slots.get("/show_available_slots/{doctor_id}")
def show_available_slots(doctor_id: int):
    db = SessionLocal()

    slots = db.query(DoctorSchedule).filter(
        DoctorSchedule.doctor_id == doctor_id,
        DoctorSchedule.is_booked == False,
        DoctorSchedule.slot_time > datetime.now()
    ).all()

    db.close()

    available_slots = [
        {
            "slot_id": slot.id,
            "slot_time": slot.slot_time
        }
        for slot in slots
    ]

    return {"available_slots": available_slots}
    