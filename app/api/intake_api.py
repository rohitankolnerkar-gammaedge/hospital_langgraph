from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from app.graphes.graph import graph
from app.helper.pdf_extractor import extract_pdf
from datetime import datetime
inta = APIRouter(prefix="/api")

@inta.post("/intake")
async def intake(
    patient_name: Optional[str] = Form(None),
    dob: Optional[str] = Form(None),
    symptoms: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    form_text: Optional[str] = Form(None),
    file: UploadFile | None = File(None),
    email: Optional[str] = Form(None),
    Appointment_time: Optional[datetime] = Form(None)
):   

    state = {}

    if form_text:
        state["raw_text"] = form_text

    elif file:
        pdf_text = extract_pdf(file)
        state["raw_text"] = pdf_text

    else:
        state = {
            "patient_name": patient_name,
            "dob": dob,
            "symptoms": symptoms,
            "phone": phone,
            "email": email,
            "appointment_status": "scheduled",
            "appointment_time": Appointment_time,
            "remainder_sent": False,
            "status":"intake_completed", 
            "comformation_sent": False,
            "summary_sent": False
        }

    result = graph.invoke(state)

    return result