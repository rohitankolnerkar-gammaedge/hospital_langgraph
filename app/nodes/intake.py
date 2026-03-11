from app.graphes.state import ClinicState
import re

def intake_node(state: ClinicState):
    text = state.get("raw_text")

    if not text:
        return {}

    name = re.search(r"Name:\s*(.*)", text)
    dob = re.search(r"DOB:\s*(.*)", text)
    symptoms = re.search(r"Symptoms:\s*(.*)", text)
    phone = re.search(r"Phone:\s*(.*)", text)

    return {
        "patient_name": name.group(1) if name else None,
        "dob": dob.group(1) if dob else None,
        "symptoms": symptoms.group(1) if symptoms else None,
        "phone": phone.group(1) if phone else None,
        "status": "intake_completed"
    }