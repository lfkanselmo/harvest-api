from src.application.ports.data_source import DataSource
from src.application.use_cases.check_sources_health import CheckSourcesHealthUseCase
from src.domain.value_objects import Metric, MetricStatus


class _HealthySource(DataSource):
    source_name = "Sana"

    async def fetch(self) -> list[Metric]:
        return [Metric(name="x", value=1.0, unit="", status=MetricStatus.OK)]


class _DegradedSource(DataSource):
    source_name = "Degradada"

    async def fetch(self) -> list[Metric]:
        return [Metric.unavailable(name="x")]


class _FailingSource(DataSource):
    source_name = "Caida"

    async def fetch(self) -> list[Metric]:
        raise TimeoutError("no responde")


async def test_execute_reports_health_per_source() -> None:
    use_case = CheckSourcesHealthUseCase([_HealthySource(), _DegradedSource(), _FailingSource()])

    results = await use_case.execute()

    assert {result.name: result.healthy for result in results} == {
        "Sana": True,
        "Degradada": False,
        "Caida": False,
    }
