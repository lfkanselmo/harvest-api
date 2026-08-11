from pathlib import Path
from uuid import UUID

from src.application.use_cases.generate_and_deliver_report import GenerateAndDeliverReportUseCase
from src.domain.models import Report
from src.infrastructure.adapters.mock_weather_adapter import MockWeatherAdapter


class FakeExporter:
    def export(self, report: Report) -> bytes:
        return b"%PDF-fake"


class FakeRepository:
    def __init__(self) -> None:
        self.saved: list[Report] = []

    async def save(self, report: Report, pdf_path: Path) -> None:
        self.saved.append(report)

    async def list_recent(self, limit: int) -> list[Report]:
        return list(self.saved[:limit])

    async def get_pdf_path(self, report_id: UUID) -> Path | None:
        return None


class FakeNotifier:
    def __init__(self) -> None:
        self.sent: list[Report] = []

    async def send(self, report: Report, pdf_bytes: bytes) -> None:
        self.sent.append(report)


class FailingNotifier:
    async def send(self, report: Report, pdf_bytes: bytes) -> None:
        raise RuntimeError("smtp caido")


async def test_execute_exports_saves_and_notifies(tmp_path: Path) -> None:
    repository = FakeRepository()
    notifier = FakeNotifier()
    use_case = GenerateAndDeliverReportUseCase(
        sources=[MockWeatherAdapter()],
        exporter=FakeExporter(),
        repository=repository,
        notifier=notifier,
        reports_dir=tmp_path,
    )

    report = await use_case.execute()

    assert repository.saved == [report]
    assert notifier.sent == [report]
    assert (tmp_path / f"{report.id}.pdf").exists()


async def test_execute_keeps_the_saved_report_even_if_notifier_fails(tmp_path: Path) -> None:
    repository = FakeRepository()
    use_case = GenerateAndDeliverReportUseCase(
        sources=[MockWeatherAdapter()],
        exporter=FakeExporter(),
        repository=repository,
        notifier=FailingNotifier(),
        reports_dir=tmp_path,
    )

    report = await use_case.execute()

    assert repository.saved == [report]
