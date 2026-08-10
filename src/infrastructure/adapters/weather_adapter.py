import logging

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.application.ports.data_source import DataSource
from src.domain.value_objects import Metric, MetricStatus

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

logger = logging.getLogger(__name__)


class WeatherAdapter(DataSource):
    def __init__(
        self,
        latitude: float,
        longitude: float,
        timeout_seconds: float = 5.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._latitude = latitude
        self._longitude = longitude
        self._timeout_seconds = timeout_seconds
        self._transport = transport

    async def fetch(self) -> list[Metric]:
        try:
            current = (await self._fetch_with_retry())["current"]
        except httpx.HTTPError:
            logger.warning("WeatherAdapter no pudo obtener datos", exc_info=True)
            return [
                Metric.unavailable(name="temp_c", unit="°C"),
                Metric.unavailable(name="humidity_pct", unit="%"),
            ]
        return [
            Metric(
                name="temp_c",
                value=current["temperature_2m"],
                unit="°C",
                status=MetricStatus.OK,
            ),
            Metric(
                name="humidity_pct",
                value=current["relative_humidity_2m"],
                unit="%",
                status=MetricStatus.OK,
            ),
        ]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.05),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True,
    )
    async def _fetch_with_retry(self) -> dict[str, dict[str, float]]:
        async with httpx.AsyncClient(
            timeout=self._timeout_seconds, transport=self._transport
        ) as client:
            response = await client.get(
                OPEN_METEO_URL,
                params={
                    "latitude": self._latitude,
                    "longitude": self._longitude,
                    "current": "temperature_2m,relative_humidity_2m",
                },
            )
            response.raise_for_status()
            data: dict[str, dict[str, float]] = response.json()
            return data
