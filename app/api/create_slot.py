from fastapi import APIRouter, Depends
from datetime import datetime
from pydantic import BaseModel
from app.db.db_config import SessionLocal
from app.db.models import DoctorSchedule

router = APIRouter()

class SlotCreate(BaseModel):
    doctor_id: int
    slot_time: datetime


@router.post("/add-slot")
def add_slot(data: SlotCreate):

    db = SessionLocal()

    slot = DoctorSchedule(
        doctor_id=data.doctor_id,
        slot_time=data.slot_time,
        is_booked=False
    )

    db.add(slot)
    db.commit()
    db.refresh(slot)
    db.close()

    return {
        "message": "Slot added successfully",
        "slot_id": slot.id,
        "doctor_id": slot.doctor_id,
        "slot_time": slot.slot_time
    }