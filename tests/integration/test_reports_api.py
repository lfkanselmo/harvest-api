from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from src.domain.models import Report, ReportPeriod
from src.domain.value_objects import Metric, MetricStatus
from src.infrastructure.adapters.mock_news_adapter import MockNewsAdapter
from src.infrastructure.adapters.mock_weather_adapter import MockWeatherAdapter
from src.infrastructure.api.dependencies import (
    build_generate_and_deliver_use_case,
    get_data_sources,
    get_report_repository,
)
from src.infrastructure.api.main import app
from src.infrastructure.config import settings

pytestmark = pytest.mark.integration


def _report() -> Report:
    return Report(
        generated_at=datetime.now(UTC),
        period=ReportPeriod.DAILY,
        metrics=[Metric(name="temp_c", value=22.5, unit="°C", status=MetricStatus.OK)],
    )


class _FakeUseCase:
    async def execute(self, period: ReportPeriod = ReportPeriod.DAILY) -> Report:
        return _report()


class _FakeRepository:
    def __init__(self, reports: list[Report]) -> None:
        self._reports = reports

    async def save(self, report: Report, pdf_path: Path) -> None:
        self._reports.append(report)

    async def list_recent(self, limit: int) -> list[Report]:
        return self._reports[:limit]

    async def get_pdf_path(self, report_id: UUID) -> Path | None:
        return None


@pytest.fixture(autouse=True)
def _override_dependencies() -> Iterator[None]:
    app.dependency_overrides[build_generate_and_deliver_use_case] = lambda: _FakeUseCase()
    app.dependency_overrides[get_report_repository] = lambda: _FakeRepository([_report()])
    app.dependency_overrides[get_data_sources] = lambda: [MockWeatherAdapter(), MockNewsAdapter()]
    yield
    app.dependency_overrides.clear()


async def _client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def test_reports_endpoints_require_a_valid_api_key() -> None:
    async with await _client() as client:
        response = await client.get("/api/v1/reports")

    assert response.status_code == 401


async def test_generate_report_with_a_valid_api_key() -> None:
    async with await _client() as client:
        response = await client.post(
            "/api/v1/reports/generate", headers={"X-API-Key": settings.api_key}
        )

    assert response.status_code == 200
    assert response.json()["period"] == "daily"


async def test_list_reports_with_a_valid_api_key() -> None:
    async with await _client() as client:
        response = await client.get(
            "/api/v1/reports", headers={"X-API-Key": settings.api_key}
        )

    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_sources_health_is_public_and_reports_each_source() -> None:
    async with await _client() as client:
        response = await client.get("/api/v1/health/sources")

    assert response.status_code == 200
    names_and_status = {item["name"]: item["status"] for item in response.json()}
    assert names_and_status == {"Clima": "ok", "Noticias": "ok"}
