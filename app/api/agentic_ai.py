from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
import json
import re

from app.helper.remainder_job import reminder_job
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from app.llm import get_llm
from app.helper.llm_send_remainder import send_reminder
agen = APIRouter()
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.start()
def extract_mcp_text(result):
    if result and result.content:
        return result.content[0].text.strip()
    return ""


def parse_extracted_text_to_intake(text: str) -> dict:
    data = {
        "patient_name": None,
        "dob": None,
        "symptoms": None,
        "phone": None,
        "email": None
    }

    patterns = {
        "patient_name": r"Name:\s*(.+)",
        "dob": r"DOB:\s*(.+)",
        "symptoms": r"Symptoms:\s*(.+)",
        "phone": r"Phone:\s*(.+)",
        "email": r"Email:\s*(.+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data[key] = match.group(1).strip()

    return data



def normalize_slots(raw_slots):
    normalized = []
    for slot in raw_slots:
        slot_id = slot.get("slot_id") or slot.get("id")
        if not slot_id:
            continue

        normalized.append({
            "slot_id": slot_id,
            "time": slot.get("time") or slot.get("slot_time")
        })
    return normalized


async def llm_decide(llm, state):
    prompt = f"""
You are a medical scheduling agent.

State:
{json.dumps(state, indent=2)}

TOOLS:
- register_patient
- show_available_slots
- add_slot
- select_slot
- send_confirmation

Rules:
- If patient_id is null → register_patient
- If slots unknown → show_available_slots
- If slots empty → add_slot
- If slot not selected → select_slot
- If booked and confirmation not sent → send_confirmation
- Otherwise → DONE

Return JSON:
{{ "action": "", "data": {{}} }}
"""

    response = llm.invoke(prompt)

    try:
        return json.loads(response)
    except:
        return {"action": "INVALID", "data": {}}


@agen.post("/agent")
async def agent(
    user_input: Optional[str] = Form(None),
    file: UploadFile | None = File(None)
):

    state = {
        "input": "",
        "patient_id": None,
        "appointment_status": None,
        "available_slots": None,
        "slot_id": None,
        "doctor_id": 1,
        "confirmation_sent": False,
        "appointment_time": None,
        "appointment_id":None
    }

    llm = get_llm()

    async with sse_client("http://localhost:8001/sse") as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()

            
            if file:
                file_bytes = await file.read()

                result = await session.call_tool(
                    "extract_pdf",
                    {
                        "filename": file.filename,
                        "content": file_bytes
                    }
                )

                extracted_text = extract_mcp_text(result)
                state["input"] = parse_extracted_text_to_intake(extracted_text)

            elif user_input:
                state["input"] = user_input

            else:
                return {"error": "No input provided"}

            
            for step in range(10):

                print(f"\nSTEP {step}")
                print("STATE:", state)

                decision = await llm_decide(llm, state)
                action = decision.get("action")
                data = decision.get("data", {})

                print("LLM DECIDED:", action)

                
                if action in ["DONE", "INVALID", None]:

                    if state["patient_id"] is None:
                        action = "register_patient"

                    elif state["available_slots"] is None:
                        action = "show_available_slots"

                    elif state["available_slots"] == []:
                        action = "add_slot"

                    elif state["slot_id"] is None:
                        action = "select_slot"

                    elif state["appointment_status"] == "booked" and not state["confirmation_sent"]:
                        action = "send_confirmation"

                    else:
                        break

                if action not in [
                    "register_patient",
                    "show_available_slots",
                    "add_slot",
                    "select_slot",
                    "send_confirmation"
                ]:
                    break

                
                if action == "register_patient":
                    data = state["input"]

                elif action == "show_available_slots":
                    data = {"doctor_id": state["doctor_id"]}

                elif action == "add_slot":
                    data = {
                        "data": {
                            "doctor_id": state["doctor_id"],
                            "slot_time": "2026-03-20 10:00"
                        }
                    }

                elif action == "select_slot":
                    if not state["available_slots"]:
                        break

                    slot = state["available_slots"][0]

                    
                    if not state["appointment_time"]:
                        state["appointment_time"] = slot.get("time")

                    data = {
                        "patient_id": state["patient_id"],
                        "slot_id": slot["slot_id"],
                        "doctor_id": state["doctor_id"]
                    }

                elif action == "send_confirmation":

                    
                    if not state["appointment_time"]:
                        print("Missing appointment_time, stopping")
                        break

                    data = {
                        "email": state["input"]["email"],
                        "appointment_time": state["appointment_time"]
                    }

                
                result = await session.call_tool(action, data)
                output = extract_mcp_text(result)

                print("TOOL OUTPUT:", output)

                if "Error executing tool" in output:
                    break

                try:
                    parsed = json.loads(output)
                except:
                    parsed = {}

               
                if action == "register_patient":
                    state["patient_id"] = parsed.get("patient_id")

                elif action == "show_available_slots":
                    raw_slots = parsed.get("available_slots", [])
                    state["available_slots"] = normalize_slots(raw_slots)

                elif action == "add_slot":
                    state["available_slots"] = normalize_slots([parsed])

                elif action == "select_slot":
                    state["appointment_status"] = parsed.get("appointment_status", "booked")
                    state['appointment_id']=parsed.get('appointment_id',1)
                    state["slot_id"] = data["slot_id"]

                    
                    if "appointment_time" in parsed:
                        state["appointment_time"] = parsed["appointment_time"]

                elif action == "send_confirmation":
                    state["confirmation_sent"] = True


                    

                    scheduler.add_job(

                        send_reminder,
                        "interval",
                        days=1,
                        args=[state['input']['email'],state["appointment_time"],state['input']['patient_name'],state['appointment_id']]
                    )

                    

                if state["confirmation_sent"]:
                    print("FLOW COMPLETE")
                    break

                print("UPDATED STATE:", state)

    return {
        "status": state["appointment_status"],
        "state": state
    }