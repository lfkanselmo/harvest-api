import pytest
from src.domain.models import ReportPeriod
from src.infrastructure.pdf.report_factory import ReportFactory


@pytest.mark.parametrize(
    ("period", "expected_template"),
    [
        (ReportPeriod.DAILY, "report_daily.html"),
        (ReportPeriod.WEEKLY, "report_weekly.html"),
    ],
)
def test_template_for_selects_the_right_template(
    period: ReportPeriod, expected_template: str
) -> None:
    assert ReportFactory().template_for(period) == expected_template
