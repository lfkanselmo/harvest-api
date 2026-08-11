from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from src.domain.models import Report, ReportPeriod
from src.domain.value_objects import Metric, MetricStatus
from src.infrastructure.persistence.orm_models import Base
from src.infrastructure.persistence.sqlite_report_repository import SqliteReportRepository

pytestmark = pytest.mark.integration


async def _repository() -> SqliteReportRepository:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    return SqliteReportRepository(async_sessionmaker(engine, expire_on_commit=False))


def _report() -> Report:
    return Report(
        generated_at=datetime.now(UTC),
        period=ReportPeriod.DAILY,
        metrics=[
            Metric(name="temp_c", value=22.5, unit="°C", status=MetricStatus.OK),
            Metric.unavailable(name="Noticias"),
        ],
    )


async def test_save_and_list_recent_round_trips_a_report() -> None:
    repository = await _repository()
    report = _report()

    await repository.save(report, Path(f"/tmp/{report.id}.pdf"))
    recent = await repository.list_recent(limit=10)

    assert recent == [report]


async def test_get_pdf_path_returns_the_stored_path() -> None:
    repository = await _repository()
    report = _report()
    pdf_path = Path(f"/tmp/{report.id}.pdf")

    await repository.save(report, pdf_path)

    assert await repository.get_pdf_path(report.id) == pdf_path


async def test_get_pdf_path_returns_none_for_an_unknown_report() -> None:
    repository = await _repository()

    assert await repository.get_pdf_path(uuid4()) is None
