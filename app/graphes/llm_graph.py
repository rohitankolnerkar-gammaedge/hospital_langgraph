from .state import ClinicState
from app.nodes.intake import intake_node
from app.nodes.create_patient_record import create_patient_record

from app.nodes.send_conformation import send_conformation
from app.nodes.send_remainder import send_reminder
from langgraph.checkpoint.memory import MemorySaver

from langgraph.graph import StateGraph, END
memory = MemorySaver()


workflow = StateGraph(ClinicState)


workflow.add_node("intake_node", intake_node)
workflow.add_node("create_patient_record", create_patient_record)




workflow.set_entry_point("intake_node")


workflow.add_edge("intake_node", "create_patient_record")

workflow.add_edge("create_patient_record", END)




graph = workflow.compile(checkpointer=memory)