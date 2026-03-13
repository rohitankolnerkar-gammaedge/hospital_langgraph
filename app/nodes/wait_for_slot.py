from langgraph.types import interrupt
from app.graphes.state import ClinicState

def wait_for_appointment_api(state: ClinicState):

    response = interrupt({
        "event": "WAIT_FOR_APPOINTMENT_API",
        "patient_id": state["patient_id"]
    })

    return {
        "appointment_time": response["appointment_time"]
    }