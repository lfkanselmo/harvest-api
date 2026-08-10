import feedparser
from src.domain.value_objects import MetricStatus
from src.infrastructure.adapters.news_adapter import NewsAdapter


def _parse_ok(url: str) -> feedparser.FeedParserDict:
    parsed = feedparser.FeedParserDict()
    parsed.bozo = 0
    parsed.entries = [{"title": "a"}, {"title": "b"}, {"title": "c"}]
    return parsed


def _parse_broken(url: str) -> feedparser.FeedParserDict:
    parsed = feedparser.FeedParserDict()
    parsed.bozo = 1
    parsed.entries = []
    return parsed


async def test_fetch_counts_headlines_on_success() -> None:
    adapter = NewsAdapter(feed_url="https://example.com/rss", parse_fn=_parse_ok)

    metrics = await adapter.fetch()

    assert metrics[0].name == "headline_count"
    assert metrics[0].value == 3.0
    assert metrics[0].status is MetricStatus.OK


async def test_fetch_degrades_when_feed_is_broken() -> None:
    adapter = NewsAdapter(feed_url="https://example.com/rss", parse_fn=_parse_broken)

    metrics = await adapter.fetch()

    assert metrics[0].status is MetricStatus.UNAVAILABLE
