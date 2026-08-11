from src.application.ports.data_source import DataSource
from src.application.use_cases.generate_report import GenerateReportUseCase
from src.domain.models import ReportPeriod
from src.domain.value_objects import Metric, MetricStatus
from src.infrastructure.adapters.mock_news_adapter import MockNewsAdapter
from src.infrastructure.adapters.mock_weather_adapter import MockWeatherAdapter


class FailingDataSource(DataSource):
    source_name = "Fuente de prueba"

    async def fetch(self) -> list[Metric]:
        raise TimeoutError("la fuente no respondio a tiempo")


async def test_execute_is_indifferent_to_which_data_source_it_receives() -> None:
    use_case = GenerateReportUseCase()

    report_a = await use_case.execute([MockWeatherAdapter()])
    report_b = await use_case.execute([MockNewsAdapter()])

    assert report_a.period is ReportPeriod.DAILY
    assert report_b.period is ReportPeriod.DAILY
    assert len(report_a.metrics) > 0
    assert len(report_b.metrics) > 0


async def test_execute_combines_metrics_from_multiple_sources() -> None:
    use_case = GenerateReportUseCase()

    report = await use_case.execute([MockWeatherAdapter(), MockNewsAdapter()])

    names = {metric.name for metric in report.metrics}
    assert "temp_c" in names
    assert "headline_count" in names


async def test_execute_degrades_a_failing_source_instead_of_crashing() -> None:
    use_case = GenerateReportUseCase()

    report = await use_case.execute([MockWeatherAdapter(), FailingDataSource()])

    assert report.has_unavailable_metrics is True
    fallback = next(m for m in report.metrics if m.name == "Fuente de prueba")
    assert fallback.status is MetricStatus.UNAVAILABLE
