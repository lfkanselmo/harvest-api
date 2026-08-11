import logging

from src.domain.models import Report

logger = logging.getLogger(__name__)


class NullNotifier:
    async def send(self, report: Report, pdf_bytes: bytes) -> None:
        logger.warning(
            "SMTP no configurado: el informe %s no fue enviado por correo", report.id
        )
