from fastapi import APIRouter, UploadFile, File, Form,HTTPException
from typing import Optional
from app.db.models import PatientRecord
from app.db.models import Appointment

from app.db.db_config import SessionLocal
from app.graphes.graph2 import graph2


from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

enter_docter = APIRouter(prefix="/api")
@enter_docter.post("/enter_docter_pres/{patient_name}")
async def enter_docter_pres(
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
    appointment =  db.query(Appointment).filter_by(patient_id=patient.id).first()
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
        file_bytes = await file.read()
        try:
            async with sse_client("http://localhost:8001/sse") as (read, write):

                async with ClientSession(read, write) as session:
                    await session.initialize()

                   
                    pdf_text_result = await session.call_tool(
                        "extract_pdf",
                        {"filename": file.filename, "content": file_bytes}
                    )
                    pdf_text = pdf_text_result.result if hasattr(pdf_text_result, "result") else str(pdf_text_result)
                    state["raw_text"] = pdf_text
                    print("Extracted Text:", pdf_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"MCP session or PDF extraction failed: {e}")

    else:
        db.close()
        return {"error": "No doctor notes provided"}
    result = await graph2.ainvoke(state)
    return {"message": "Doctor notes entered successfully"}
    
    