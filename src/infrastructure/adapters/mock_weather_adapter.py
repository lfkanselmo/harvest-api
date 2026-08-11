from src.application.ports.data_source import DataSource
from src.domain.value_objects import Metric, MetricStatus


class MockWeatherAdapter(DataSource):
    source_name = "Clima"

    async def fetch(self) -> list[Metric]:
        return [
            Metric(name="temp_c", value=22.5, unit="°C", status=MetricStatus.OK),
            Metric(name="humidity_pct", value=58.0, unit="%", status=MetricStatus.OK),
        ]
