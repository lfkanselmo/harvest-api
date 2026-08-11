from datetime import UTC, datetime
from uuid import UUID

from src.domain.models import Report, ReportPeriod
from src.domain.value_objects import Metric, MetricStatus


def test_report_gets_a_unique_id_by_default() -> None:
    metrics = [Metric(name="temp_c", value=22.5, unit="°C", status=MetricStatus.OK)]
    report_a = Report(generated_at=datetime.now(UTC), period=ReportPeriod.DAILY, metrics=metrics)
    report_b = Report(generated_at=datetime.now(UTC), period=ReportPeriod.DAILY, metrics=metrics)

    assert isinstance(report_a.id, UUID)
    assert report_a.id != report_b.id


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
