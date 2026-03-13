from .state import ClinicState
from app.nodes.intake import intake_node
from app.nodes.create_patient_record import create_patient_record
from app.nodes.wait_for_slot import wait_for_appointment_api
from app.nodes.send_conformation import send_conformation
from app.nodes.send_remainder import send_reminder
from langgraph.checkpoint.memory import MemorySaver

from langgraph.graph import StateGraph, END
memory = MemorySaver()
def decide_next_step(state):
    if state.get("summary_sent") == True:
        return "sent"
    return "not_sent"

workflow = StateGraph(ClinicState)


workflow.add_node("intake_node", intake_node)
workflow.add_node("create_patient_record", create_patient_record)
workflow.add_node("wait_for_appointment_api", wait_for_appointment_api)
workflow.add_node("send_conformation", send_conformation)
workflow.add_node("send_reminder", send_reminder)


workflow.set_entry_point("intake_node")


workflow.add_edge("intake_node", "create_patient_record")
workflow.add_edge("create_patient_record", "wait_for_appointment_api")
workflow.add_edge("wait_for_appointment_api", "send_conformation")
workflow.add_edge("send_conformation", "send_reminder")
workflow.add_edge("send_reminder", END)




graph = workflow.compile(checkpointer=memory)