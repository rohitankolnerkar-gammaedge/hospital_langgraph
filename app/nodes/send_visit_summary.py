from langchain_core.prompts import ChatPromptTemplate
from app.llm import get_llm
from app.graphes.state import ClinicState
from app.helper.send_email import send_email_tool
llm = get_llm()


def create_llm_chain():

    prompt = ChatPromptTemplate.from_template("""
You are a medical documentation assistant.

Your task is to convert raw doctor notes into a clear and structured clinical summary.

Instructions:
- Only use information present in the notes.
- Do not invent medical details.
- Keep the summary concise and professional.
- If information is missing, write "Not specified".

Output Format:

Patient Visit Summary

Chief Complaint:
<main patient issue>

Symptoms:
<list symptoms mentioned>

Assessment / Diagnosis:
<doctor’s assessment if mentioned>

Treatment / Medication:
<medications or treatments prescribed>

Doctor Notes Summary:
<short paragraph summarizing the visit>

Follow-up Instructions:
<any follow up advice or tests>

Doctor Notes:
{doctor_notes}
""")

    chain = prompt | llm
    return chain


def send_visit_summary(state: ClinicState):

    doctor_notes = state.get("doctor_notes")

    chain = create_llm_chain()

    summary = chain.invoke({
        "doctor_notes": doctor_notes
    })
    if send_email_tool(state.get("email"), "Your Visit Summary", summary.content):
        print("Generated visit summary:")
        print(summary)
        return {"summary": summary.content, "status": "summary_sent", "summary_sent": True}
    else:
        return {"summary": None, "status": "summary_failed", "summary_sent": False}