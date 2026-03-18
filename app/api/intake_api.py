from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.graphes.graph import graph
from datetime import datetime
import uuid
import asyncio


from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

thread_id = str(uuid.uuid4())
inta = APIRouter(prefix="/api")

def extract_mcp_text(response):
    if response and response.content:
        return response.content[0].text.strip()
    return ""

@inta.post("/intake")
async def intake(
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