from .state import ClinicState
from app.nodes.intake import intake_node
from app.nodes.create_patient_record import create_patient_record
from app.nodes.apointment import schedule_appointment
from app.nodes.send_conformation import send_conformation
from app.nodes.send_remainder import send_reminder

from langgraph.graph import StateGraph, END

def decide_next_step(state):
    if state.get("summary_sent") == True:
        return "sent"
    return "not_sent"

workflow = StateGraph(ClinicState)


workflow.add_node("intake_node", intake_node)
workflow.add_node("create_patient_record", create_patient_record)
workflow.add_node("schedule_appointment", schedule_appointment)
workflow.add_node("send_conformation", send_conformation)
workflow.add_node("send_reminder", send_reminder)


workflow.set_entry_point("intake_node")


workflow.add_edge("intake_node", "create_patient_record")
workflow.add_edge("create_patient_record", "schedule_appointment")
workflow.add_edge("schedule_appointment", "send_conformation")
workflow.add_edge("send_conformation", "send_reminder")
workflow.add_edge("send_reminder", END)




graph = workflow.compile()