import asyncio
from dataclasses import dataclass

from src.application.ports.data_source import DataSource
from src.domain.value_objects import MetricStatus


@dataclass(frozen=True)
class SourceHealth:
    name: str
    healthy: bool


class CheckSourcesHealthUseCase:
    def __init__(self, sources: list[DataSource]) -> None:
        self._sources = sources

    async def execute(self) -> list[SourceHealth]:
        results = await asyncio.gather(
            *(source.fetch() for source in self._sources), return_exceptions=True
        )
        return [
            SourceHealth(name=source.source_name, healthy=self._is_healthy(result))
            for source, result in zip(self._sources, results, strict=True)
        ]

    @staticmethod
    def _is_healthy(result: object) -> bool:
        if isinstance(result, BaseException) or not isinstance(result, list) or not result:
            return False
        return all(metric.status is MetricStatus.OK for metric in result)
