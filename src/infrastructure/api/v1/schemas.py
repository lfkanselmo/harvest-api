from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.application.use_cases.check_sources_health import SourceHealth
from src.domain.models import Report, ReportPeriod


class MetricOut(BaseModel):
    name: str
    value: float | None
    unit: str
    status: str


class SourceHealthOut(BaseModel):
    name: str
    status: str

    @classmethod
    def from_domain(cls, source_health: SourceHealth) -> SourceHealthOut:
        return cls(name=source_health.name, status="ok" if source_health.healthy else "unavailable")


class ReportOut(BaseModel):
    id: UUID
    generated_at: datetime
    period: ReportPeriod
    has_unavailable_metrics: bool
    metrics: list[MetricOut]

    @classmethod
    def from_domain(cls, report: Report) -> ReportOut:
        return cls(
            id=report.id,
            generated_at=report.generated_at,
            period=report.period,
            has_unavailable_metrics=report.has_unavailable_metrics,
            metrics=[
                MetricOut(name=metric.name, value=metric.value, unit=metric.unit,
                           status=metric.status.value)
                for metric in report.metrics
            ],
        )
