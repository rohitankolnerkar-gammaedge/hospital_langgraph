import smtplib
from email.message import EmailMessage

def send_email_tool(to_email, subject, body):

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = "rohit.ankolnerkar@gammaedge.io"
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("rohit.ankolnerkar@gammaedge.io", "aong pheh bcxx kegx")
        server.send_message(msg)

    return {"status": "sent"}