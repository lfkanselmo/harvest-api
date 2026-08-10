import httpx
from src.domain.value_objects import MetricStatus
from src.infrastructure.adapters.weather_adapter import WeatherAdapter


def _transport(status_code: int) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        if status_code != 200:
            return httpx.Response(status_code)
        return httpx.Response(
            200,
            json={"current": {"temperature_2m": 21.4, "relative_humidity_2m": 63.0}},
        )

    return httpx.MockTransport(handler)


async def test_fetch_returns_metrics_on_success() -> None:
    adapter = WeatherAdapter(latitude=4.71, longitude=-74.07, transport=_transport(200))

    metrics = await adapter.fetch()

    assert metrics[0].name == "temp_c"
    assert metrics[0].value == 21.4
    assert metrics[0].status is MetricStatus.OK
    assert metrics[1].name == "humidity_pct"
    assert metrics[1].value == 63.0


async def test_fetch_degrades_after_retries_are_exhausted() -> None:
    adapter = WeatherAdapter(latitude=4.71, longitude=-74.07, transport=_transport(503))

    metrics = await adapter.fetch()

    assert all(metric.status is MetricStatus.UNAVAILABLE for metric in metrics)
