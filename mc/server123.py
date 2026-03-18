from mcp.server.fastmcp import FastMCP

import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
load_dotenv()
import pdfplumber
import asyncio
import io
from fastapi import  UploadFile, File, Form,HTTPException
from typing import Optional
from app.db.models import PatientRecord
from app.db.models import Appointment

from app.db.db_config import SessionLocal
from app.graphes.graph2 import graph2


from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

from datetime import datetime
from pydantic import BaseModel
from app.db.db_config import SessionLocal
from app.db.models import DoctorSchedule


from app.db.db_config import SessionLocal
from app.db.models import Appointment, DoctorSchedule, PatientRecord
from datetime import datetime
from langgraph.types import Command
from app.graphes.llm_graph2 import graph2
from app.api.intake_api import thread_id

from app.db.db_config import SessionLocal
from app.db.models import Appointment,DoctorSchedule
from datetime import datetime, timedelta
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.graphes.llm_graph import graph
from datetime import datetime
import uuid
import asyncio


from fastapi import HTTPException

from app.graphes.state import ClinicState
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

server = FastMCP("clinic-tools",port=8001 )


@server.tool()
async def extract_pdf(filename: str, content: bytes):

    filename = filename.lower()

    def process_file():

        if filename.endswith(".txt"):
            return content.decode("utf-8")

        elif filename.endswith(".pdf"):
            text = ""
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text

        else:
            raise ValueError("Unsupported file type. Only PDF and TXT are allowed.")

    return await asyncio.to_thread(process_file)


@server.tool()
def send_email_tool(to_email, subject, body):

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "rohit.ankolnerkar@gammaedge.io"
    msg["To"] = to_email
    msg.set_content(body)
    send_email=os.getenv("send_email_api")
    sender_email=os.getenv("sender_email")
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, send_email)
        server.send_message(msg)

    return {"status": "sent"}


thread_id = str(uuid.uuid4())
inta = APIRouter(prefix="/api")

def extract_mcp_text(response):
    if response and response.content:
        return response.content[0].text.strip()
    return ""

@server.tool()
async def register_patient(
    patient_name: Optional[str] = Form(None),
    dob: Optional[str] = Form(None),
    symptoms: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    form_text: Optional[str] = Form(None),
    file: UploadFile | None = File(None),
    email: Optional[str] = Form(None),
):
    state = {}

    if form_text:
        state["raw_text"] = form_text

   
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
                    
                    pdf_text = extract_mcp_text(pdf_text_result)
                    state["raw_text"] = pdf_text
                    print("Extracted Text:", pdf_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"MCP session or PDF extraction failed: {e}")

   
    else:
        state = {
            "patient_name": patient_name,
            "dob": dob,
            "symptoms": symptoms,
            "phone": phone,
            "email": email,
            "appointment_status": "scheduled",
            "remainder_sent": False,
            "status": "intake_completed",
            "comformation_sent": False,
            "summary_sent": False,
            "raw_text": ""
        }

    
    result = await graph.ainvoke(
    state,
    config={"configurable": {"thread_id": thread_id}}
)
    return result
    




@server.tool()
async def select_slot(patient_id: int, slot_id: int, doctor_id: int):

    db = SessionLocal()

   
    patient =  db.query(PatientRecord).filter_by(id=patient_id).first()

    if not patient:
        db.close()
        return {"error": "Patient not found"}

  
    doctor_slot =  db.query(DoctorSchedule).filter_by(
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

    
    result = await graph.ainvoke(
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





@server.tool()
def show_available_slots(doctor_id: int):
    db = SessionLocal()
    print("DB PATH:", os.path.abspath("clinic.db"))
    print("Writable:", os.access("clinic.db", os.W_OK))
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
    





class SlotCreate(BaseModel):
    doctor_id: int
    slot_time: datetime


@server.tool()
def add_slot(data: SlotCreate):
    import os

    print("DB PATH:", os.path.abspath("clinic.db"))
    print("Writable:", os.access("clinic.db", os.W_OK))
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



@server.tool()
async def send_confirmation(email,appointment_time):
    
    email = email
    appointment_time = appointment_time

    if not email or not appointment_time:
        return {"status": "missing_info"}

    subject = "Appointment Confirmation"
    body = f"Your appointment is scheduled for {appointment_time}."
    try:
      
      async with sse_client("http://localhost:8001/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print(await session.list_tools())
            email_sent= await session.call_tool(
                "send_email_tool",
                {"to_email": email, "subject": subject,"body":body}
            )
                
            print(email_sent)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP session or PDF extraction failed: {e}")
    if email_sent:
        return {"appointment_status": "confirmed","confirmation_sent": True, "status": "confirmation_sent"}
    else:
        return {"appointment_status": "confirmation_failed","confirmation_sent": False, "status": "confirmation_failed"}


if __name__ == "__main__":
    server.run(
        transport="sse"
    )
    