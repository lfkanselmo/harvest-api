from datetime import UTC, datetime

import pytest
from src.domain.models import Report, ReportPeriod
from src.domain.value_objects import Metric, MetricStatus
from src.infrastructure.pdf.pdf_exporter import PDFExporter, format_metric_value

pytestmark = pytest.mark.integration


def test_format_metric_value_drops_decimals_for_whole_numbers() -> None:
    assert format_metric_value(5.0) == "5"
    assert format_metric_value(342.0) == "342"


def test_format_metric_value_keeps_two_decimals_otherwise() -> None:
    assert format_metric_value(22.5) == "22.50"
    assert format_metric_value(128450.75) == "128,450.75"


def _sample_report(period: ReportPeriod) -> Report:
    return Report(
        generated_at=datetime.now(UTC),
        period=period,
        metrics=[
            Metric(name="temp_c", value=22.5, unit="°C", status=MetricStatus.OK),
            Metric.unavailable(name="headline_count", unit="titulares"),
        ],
    )


def test_export_produces_a_valid_pdf_for_a_daily_report() -> None:
    pdf_bytes = PDFExporter().export(_sample_report(ReportPeriod.DAILY))

    assert pdf_bytes[:5] == b"%PDF-"
    assert len(pdf_bytes) > 1000


def test_export_produces_a_valid_pdf_for_a_weekly_report() -> None:
    pdf_bytes = PDFExporter().export(_sample_report(ReportPeriod.WEEKLY))

    assert pdf_bytes[:5] == b"%PDF-"
