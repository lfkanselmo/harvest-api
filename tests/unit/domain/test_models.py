from datetime import UTC, datetime

from src.domain.models import Report, ReportPeriod
from src.domain.value_objects import Metric, MetricStatus


def test_report_flags_unavailable_metrics() -> None:
    report = Report(
        generated_at=datetime.now(UTC),
        period=ReportPeriod.DAILY,
        metrics=[
            Metric(name="temp_c", value=22.5, unit="°C", status=MetricStatus.OK),
            Metric.unavailable(name="NewsAdapter"),
        ],
    )

    assert report.has_unavailable_metrics is True


def test_report_without_failures_is_not_flagged() -> None:
    report = Report(
        generated_at=datetime.now(UTC),
        period=ReportPeriod.DAILY,
        metrics=[Metric(name="temp_c", value=22.5, unit="°C", status=MetricStatus.OK)],
    )

    assert report.has_unavailable_metrics is False
