import pytest
from src.application.ports.data_source import DataSource
from src.domain.value_objects import Metric, MetricStatus
from src.infrastructure.adapters.mock_news_adapter import MockNewsAdapter
from src.infrastructure.adapters.mock_weather_adapter import MockWeatherAdapter

ADAPTERS: list[DataSource] = [MockWeatherAdapter(), MockNewsAdapter()]


@pytest.mark.parametrize("adapter", ADAPTERS, ids=lambda a: type(a).__name__)
async def test_any_data_source_fulfills_the_contract(adapter: DataSource) -> None:
    metrics = await adapter.fetch()

    assert len(metrics) > 0
    assert all(isinstance(metric, Metric) for metric in metrics)
    assert all(metric.status is MetricStatus.OK for metric in metrics)
