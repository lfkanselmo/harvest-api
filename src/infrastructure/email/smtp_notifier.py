import logging
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from src.domain.models import Report

logger = logging.getLogger(__name__)


class SmtpNotifier:
    def __init__(
        self,
        host: str,
        port: int,
        username: str | None,
        password: str | None,
        from_address: str,
        use_tls: bool,
        recipients: list[str],
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from_address = from_address
        self._use_tls = use_tls
        self._recipients = recipients

    async def send(self, report: Report, pdf_bytes: bytes) -> None:
        message = MIMEMultipart()
        date = report.generated_at.strftime("%Y-%m-%d")
        message["Subject"] = f"Harvest — informe {report.period.value} {date}"
        message["From"] = self._from_address
        message["To"] = ", ".join(self._recipients)
        message.attach(MIMEText("Informe ejecutivo adjunto en PDF.", "plain", "utf-8"))

        attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
        attachment.add_header(
            "Content-Disposition", "attachment", filename=f"harvest_report_{report.id}.pdf"
        )
        message.attach(attachment)

        await aiosmtplib.send(
            message,
            hostname=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            start_tls=self._use_tls,
        )
