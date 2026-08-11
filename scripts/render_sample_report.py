import asyncio
from pathlib import Path

from src.application.ports.data_source import DataSource
from src.application.use_cases.generate_report import GenerateReportUseCase
from src.domain.models import ReportPeriod
from src.domain.value_objects import Metric
from src.infrastructure.adapters.mock_news_adapter import MockNewsAdapter
from src.infrastructure.adapters.mock_weather_adapter import MockWeatherAdapter
from src.infrastructure.pdf.pdf_exporter import PDFExporter

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"


class _FailingSource(DataSource):
    source_name = "Fuente de ejemplo"

    async def fetch(self) -> list[Metric]:
        raise TimeoutError("fuente de ejemplo caida a proposito")


async def main() -> None:
    use_case = GenerateReportUseCase()
    exporter = PDFExporter()
    sources: list[DataSource] = [MockWeatherAdapter(), MockNewsAdapter(), _FailingSource()]

    OUTPUT_DIR.mkdir(exist_ok=True)

    for period, filename in (
        (ReportPeriod.DAILY, "harvest_report_sample_daily.pdf"),
        (ReportPeriod.WEEKLY, "harvest_report_sample_weekly.pdf"),
    ):
        report = await use_case.execute(sources, period=period)
        pdf_bytes = exporter.export(report)
        output_path = OUTPUT_DIR / filename
        output_path.write_bytes(pdf_bytes)
        print(f"Generado {output_path} ({len(pdf_bytes)} bytes)")


if __name__ == "__main__":
    asyncio.run(main())
