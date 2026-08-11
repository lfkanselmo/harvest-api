from typing import Protocol

from src.domain.models import Report


class ReportExporter(Protocol):
    def export(self, report: Report) -> bytes: ...
