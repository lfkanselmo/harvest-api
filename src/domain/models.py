from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from src.domain.value_objects import Metric, MetricStatus


class ReportPeriod(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"


class Report(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    generated_at: datetime
    period: ReportPeriod
    metrics: list[Metric]

    @property
    def has_unavailable_metrics(self) -> bool:
        return any(metric.status is MetricStatus.UNAVAILABLE for metric in self.metrics)
