from typing import Protocol

from src.domain.models import Report


class Notifier(Protocol):
    async def send(self, report: Report, pdf_bytes: bytes) -> None: ...
