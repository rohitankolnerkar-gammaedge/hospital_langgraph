import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
load_dotenv()

def send_email_tool(to_email, subject, body):

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "rohit.ankolnerkar@gammaedge.io"
    msg["To"] = to_email
    msg.set_content(body)
    send_email=os.getenv("send_email_api")
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("rohit.ankolnerkar@gammaedge.io", send_email)
        server.send_message(msg)

    return {"status": "sent"}