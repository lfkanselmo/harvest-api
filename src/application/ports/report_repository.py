from pathlib import Path
from typing import Protocol
from uuid import UUID

from src.domain.models import Report


class ReportRepository(Protocol):
    async def save(self, report: Report, pdf_path: Path) -> None: ...

    async def list_recent(self, limit: int) -> list[Report]: ...

    async def get_pdf_path(self, report_id: UUID) -> Path | None: ...
