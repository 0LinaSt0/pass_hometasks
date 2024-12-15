# observer/notifier.py

from observer.observer import Observer
from adapter.email_service import ExternalEmailService

class ConsoleNotifier(Observer):
    def update(self, message: str):
        print(f"ConsoleNotifier: {message}")

class EmailNotifier(Observer):
    def __init__(self, email_service: ExternalEmailService, to_address: str):
        self.email_service = email_service
        self.to_address = to_address

    def update(self, message: str):
        subject = "Motion Detection Alert"
        body = message
        self.email_service.send_email(self.to_address, subject, body)
