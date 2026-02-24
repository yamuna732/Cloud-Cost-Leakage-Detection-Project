import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = "vyamuna811@gmail.com"
SENDER_PASSWORD = "kobq fddt xqxh qdlw"
RECIPIENT_EMAIL = "yamunaprarthanaa0511@gmail.com"


def send_email(message_text):
    msg = MIMEText(message_text)
    msg["Subject"] = "Monthly Cloud Cost Savings Report"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

    print("Email sent successfully")


# local test
if __name__ == "__main__":
    test_message = "Test email from Cloud Cost Scanner SaaS"
    send_email(test_message)