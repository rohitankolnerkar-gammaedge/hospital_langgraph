from.state import ClinicState
from app.nodes.send_visit_summary import send_visit_summary
from app.nodes.get_doctor_pres import get_doctor_pres
from langgraph.graph import StateGraph, END
def decide_next_step(state):
    if state.get("summary_sent") == True:
        return "sent"
    return "not_sent"


workflow = StateGraph(ClinicState)
workflow.add_node("get_doctor_pres", get_doctor_pres)
workflow.add_node("send_visit_summary", send_visit_summary)
workflow.set_entry_point("get_doctor_pres")
workflow.add_edge("get_doctor_pres", "send_visit_summary")
workflow.add_conditional_edges(
    "send_visit_summary",
    decide_next_step,
    {
        "sent": END,
        "not_sent": "send_visit_summary"
    }
)       
graph2=workflow.compile()