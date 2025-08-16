import os
from pathlib import Path
from mailgun.client import Client

class MailGun:
    def __init__(self):
        key: str = "760a872ad0b4b170a0f332d13205ab76-16bc1610-a5ae1fb7"
        self.domain: str = "sandboxfce514c06c92469882cf761e476097d8.mailgun.org"
        self.client: Client = Client(auth=("api", key))


    def send_email(self, to, subject, text, attachment) -> None:
        # Messages
        # POST /<domain>/messages
        data = {
            "from": os.getenv("MESSAGES_FROM", "dailystocksreport@stocksai.com"),
            "to": os.getenv("MESSAGES_TO", to),
            "subject": subject,
            "text": text,
        }

        # It is strongly recommended that you open files in binary mode.
        # Because the Content-Length header may be provided for you,
        # and if it does this value will be set to the number of bytes in the file.
        # Errors may occur if you open the file in text mode.
        files = [
            (
                "attachment",
                (attachment, Path(attachment).read_bytes()),
            )
        ]

        self.client.messages.create(data=data, files=files, domain=self.domain)