from fastapi import HTTPException

from app.graphes.state import ClinicState
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
async def send_conformation(state:ClinicState):
    
    email = state.get("email")
    appointment_time = state.get("appointment_time")

    if not email or not appointment_time:
        return {"status": "missing_info"}

    subject = "Appointment Confirmation"
    body = f"Your appointment is scheduled for {appointment_time}."
    try:
      
      async with sse_client("http://localhost:8001/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print(await session.list_tools())
            email_sent= await session.call_tool(
                "send_email_tool",
                {"to_email": email, "subject": subject,"body":body}
            )
                
            print(email_sent)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP session or PDF extraction failed: {e}")
    if email_sent:
        return {"appointment_status": "confirmed","confirmation_sent": True, "status": "confirmation_sent"}
    else:
        return {"appointment_status": "confirmation_failed","confirmation_sent": False, "status": "confirmation_failed"}