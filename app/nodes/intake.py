from app.graphes.state import ClinicState
import re

def intake_node(state: ClinicState):
    text = state.get("raw_text")

    if not text:
        return {}

    name = re.search(r"Name:\s*(.+)", text)
    dob = re.search(r"DOB:\s*(.+)", text)
    symptoms = re.search(r"Symptoms:\s*(.+)", text)
    phone = re.search(r"Phone:\s*(.+)", text)
    email = re.search(r"Email:\s*(.+)", text)

    return {
        "patient_name": name.group(1).strip() if name else None,
        "dob": dob.group(1).strip() if dob else None,
        "symptoms": symptoms.group(1).strip() if symptoms else None,
        "phone": phone.group(1).strip() if phone else None,
        "email": email.group(1).strip() if email else None,
        "status": "intake_completed",
        "raw_text":" "
    }