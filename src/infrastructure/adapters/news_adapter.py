import asyncio
import logging
from collections.abc import Callable

import feedparser

from src.application.ports.data_source import DataSource
from src.domain.value_objects import Metric, MetricStatus

logger = logging.getLogger(__name__)


class NewsAdapter(DataSource):
    def __init__(
        self,
        feed_url: str,
        parse_fn: Callable[[str], feedparser.FeedParserDict] = feedparser.parse,
    ) -> None:
        self._feed_url = feed_url
        self._parse_fn = parse_fn

    async def fetch(self) -> list[Metric]:
        parsed = await asyncio.to_thread(self._parse_fn, self._feed_url)
        if parsed.bozo:
            logger.warning("NewsAdapter no pudo leer el feed %s", self._feed_url)
            return [Metric.unavailable(name="headline_count", unit="titulares")]
        return [
            Metric(
                name="headline_count",
                value=float(len(parsed.entries)),
                unit="titulares",
                status=MetricStatus.OK,
            )
        ]
