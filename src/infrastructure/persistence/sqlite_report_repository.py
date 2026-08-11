import json
from datetime import UTC
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.models import Report, ReportPeriod
from src.domain.value_objects import Metric
from src.infrastructure.persistence.orm_models import ReportOrm


class SqliteReportRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, report: Report, pdf_path: Path) -> None:
        metrics_json = json.dumps([metric.model_dump(mode="json") for metric in report.metrics])
        async with self._session_factory() as session:
            session.add(
                ReportOrm(
                    id=report.id,
                    generated_at=report.generated_at,
                    period=report.period.value,
                    metrics_json=metrics_json,
                    pdf_path=str(pdf_path),
                )
            )
            await session.commit()

    async def list_recent(self, limit: int) -> list[Report]:
        async with self._session_factory() as session:
            rows = (
                (
                    await session.execute(
                        select(ReportOrm).order_by(ReportOrm.generated_at.desc()).limit(limit)
                    )
                )
                .scalars()
                .all()
            )
        return [self._to_domain(row) for row in rows]

    async def get_pdf_path(self, report_id: UUID) -> Path | None:
        async with self._session_factory() as session:
            row = await session.get(ReportOrm, report_id)
        return Path(row.pdf_path) if row is not None else None

    def _to_domain(self, row: ReportOrm) -> Report:
        metrics = [Metric.model_validate(item) for item in json.loads(row.metrics_json)]
        # SQLite no conserva tzinfo; generated_at siempre se guarda en UTC (ver save()).
        generated_at = row.generated_at.replace(tzinfo=UTC)
        return Report(
            id=row.id,
            generated_at=generated_at,
            period=ReportPeriod(row.period),
            metrics=metrics,
        )
