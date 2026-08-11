from datetime import UTC, datetime

import pytest
from src.domain.models import Report, ReportPeriod
from src.domain.value_objects import Metric, MetricStatus
from src.infrastructure.pdf.pdf_exporter import PDFExporter

pytestmark = pytest.mark.integration


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
