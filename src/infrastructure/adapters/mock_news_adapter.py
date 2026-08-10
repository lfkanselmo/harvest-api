from src.application.ports.data_source import DataSource
from src.domain.value_objects import Metric, MetricStatus


class MockNewsAdapter(DataSource):
    async def fetch(self) -> list[Metric]:
        return [
            Metric(name="headline_count", value=5.0, unit="titulares", status=MetricStatus.OK),
        ]
