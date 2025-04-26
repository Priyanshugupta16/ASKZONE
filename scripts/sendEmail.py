import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendMail(to, subject, body):
    sender_email = "kshitijbudholiya2006@gmail.com"
    sender_password = "iykl shdr qmvm pgyy"
    
    body = body

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to

    message.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)
        return f"Activation email sent to {to}.", True
    except Exception as e:
        return f"Failed to send email. Try again after some time.", False
