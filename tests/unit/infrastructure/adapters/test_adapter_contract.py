import feedparser
import httpx
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from src.application.ports.data_source import DataSource
from src.domain.value_objects import Metric, MetricStatus
from src.infrastructure.adapters.erp_adapter import ErpAdapter
from src.infrastructure.adapters.mock_news_adapter import MockNewsAdapter
from src.infrastructure.adapters.mock_weather_adapter import MockWeatherAdapter
from src.infrastructure.adapters.news_adapter import NewsAdapter
from src.infrastructure.adapters.weather_adapter import WeatherAdapter
from src.infrastructure.persistence.orm_models import Base, InternalMetricOrm


def _weather_transport() -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"current": {"temperature_2m": 20.0, "relative_humidity_2m": 55.0}}
        )

    return httpx.MockTransport(handler)


def _news_parse_fn(url: str) -> feedparser.FeedParserDict:
    parsed = feedparser.FeedParserDict()
    parsed.bozo = 0
    parsed.entries = [{"title": "titular"}]
    return parsed


async def _seeded_erp_adapter() -> ErpAdapter:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        session.add(InternalMetricOrm(name="active_users", value=100.0, unit="usuarios"))
        await session.commit()
    return ErpAdapter(factory)


async def _all_data_sources() -> list[DataSource]:
    return [
        MockWeatherAdapter(),
        MockNewsAdapter(),
        WeatherAdapter(latitude=4.71, longitude=-74.07, transport=_weather_transport()),
        NewsAdapter(feed_url="https://example.com/rss", parse_fn=_news_parse_fn),
        await _seeded_erp_adapter(),
    ]


async def test_any_data_source_fulfills_the_contract() -> None:
    for adapter in await _all_data_sources():
        metrics = await adapter.fetch()

        assert len(metrics) > 0
        assert all(isinstance(metric, Metric) for metric in metrics)
        assert all(metric.status is MetricStatus.OK for metric in metrics)
