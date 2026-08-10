from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from src.domain.value_objects import Metric, MetricStatus


class ReportPeriod(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"


class Report(BaseModel):
    model_config = ConfigDict(frozen=True)

    generated_at: datetime
    period: ReportPeriod
    metrics: list[Metric]

    @property
    def has_unavailable_metrics(self) -> bool:
        return any(metric.status is MetricStatus.UNAVAILABLE for metric in self.metrics)
