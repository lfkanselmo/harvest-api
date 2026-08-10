import asyncio
from datetime import UTC, datetime

from src.application.ports.data_source import DataSource
from src.domain.models import Report, ReportPeriod
from src.domain.value_objects import Metric


class GenerateReportUseCase:
    async def execute(
        self, sources: list[DataSource], period: ReportPeriod = ReportPeriod.DAILY
    ) -> Report:
        results = await asyncio.gather(
            *(source.fetch() for source in sources), return_exceptions=True
        )
        metrics: list[Metric] = []
        for source, result in zip(sources, results, strict=True):
            if isinstance(result, BaseException):
                metrics.append(Metric.unavailable(name=type(source).__name__))
            else:
                metrics.extend(result)
        return Report(generated_at=datetime.now(UTC), period=period, metrics=metrics)
