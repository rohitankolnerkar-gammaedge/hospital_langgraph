from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from app.db.models import PatientRecord
from app.db.models import Appointment
from app.helper.pdf_extractor import extract_pdf
from app.db.db_config import SessionLocal
from app.graphes.graph2 import graph2

enter_docter = APIRouter(prefix="/api")
@enter_docter.post("/enter_docter_pres/{patient_name}")
def enter_docter_pres(
    patient_name: str,
    doctor_id: Optional[int] = Form(None) ,
    doctor_notes: Optional[str] = Form(None),
    file: UploadFile | None = File(None),

):
    state = {}
    db = SessionLocal()
    patient = db.query(PatientRecord).filter_by(patient_name=patient_name).first()

    if doctor_id is not None:
        state["doctor_id"] = doctor_id

    if not patient:
        db.close()
        return {"error": "Patient not found"}
    appointment = db.query(Appointment).filter_by(patient_id=patient.id).first()
    state["patient_name"] = patient_name
    state["patient_id"] = patient.id
    state["appointment_time"] = appointment.appointment_time if appointment else None
    state["symptoms"] = patient.symptoms
    state["email"] = patient.email
    state["dob"] = patient.dob
    state["phone"] = patient.phone
    state["status"] = "doctor_notes_entered"
    
    

    if doctor_notes:
        state["doctor_notes"] = doctor_notes
    elif file:
        pdf_text = extract_pdf(file)
        state["doctor_notes"] = pdf_text

    else:
        db.close()
        return {"error": "No doctor notes provided"}
    graph2.invoke(state)
    return {"message": "Doctor notes entered successfully"}
    
    