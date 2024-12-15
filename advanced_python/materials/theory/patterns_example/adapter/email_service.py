# adapter/email_service.py

import smtplib
from email.mime.text import MIMEText

class ExternalEmailService:
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_email(self, to_address: str, subject: str, body: str):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.username
        msg['To'] = to_address

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            print(f"ExternalEmailService: Email sent to {to_address} with subject '{subject}'")
        except Exception as e:
            print(f"ExternalEmailService: Failed to send email to {to_address}. Error: {e}")
