from fastapi import APIRouter
from app.db.db_config import SessionLocal
from app.db.models import Appointment, DoctorSchedule, PatientRecord
from datetime import datetime
from langgraph.types import Command
from app.graphes.graph import graph
from app.api.intake_api import thread_id

select_sl = APIRouter(prefix="/api")

@select_sl.post("/select_slot/{patient_id}/{slot_time}/{doctor_id}")
def select_slot(patient_id: int, slot_id: int, doctor_id: int):

    db = SessionLocal()

   
    patient = db.query(PatientRecord).filter_by(id=patient_id).first()

    if not patient:
        db.close()
        return {"error": "Patient not found"}

  
    doctor_slot = db.query(DoctorSchedule).filter_by(
        doctor_id=doctor_id,
        id=slot_id
    ).first()

    if not doctor_slot:
        db.close()
        return {"error": "Slot not found"}

    if doctor_slot.is_booked:
        db.close()
        return {"error": "Slot already booked"}

    slot_time=doctor_slot.slot_time
    appointment = Appointment(
        patient_id=patient_id,
        appointment_time=slot_time,
        status="slot_selected"
    )

    db.add(appointment)

   
    doctor_slot.is_booked = True

    db.commit()
    db.refresh(appointment)

    db.close()

    
    result = graph.invoke(
        Command(
            resume={
                "appointment_time": slot_time
            }
        ),
        config={"configurable": {"thread_id": thread_id}}
    )

    return {
        "result": result,
        "appointment_id": appointment.id,
        "appointment_time": slot_time,
        "appointment_status": "booked"
    }