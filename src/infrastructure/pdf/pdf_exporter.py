from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from src.domain.models import Report
from src.infrastructure.pdf.report_factory import ReportFactory

TEMPLATES_DIR = Path(__file__).parent / "templates"


def format_metric_value(value: float) -> str:
    if value == int(value):
        return f"{value:,.0f}"
    return f"{value:,.2f}"


class PDFExporter:
    def __init__(self, factory: ReportFactory | None = None) -> None:
        self._factory = factory or ReportFactory()
        self._environment = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=select_autoescape(["html"]),
        )
        self._environment.filters["metric_value"] = format_metric_value

    def export(self, report: Report) -> bytes:
        template = self._environment.get_template(self._factory.template_for(report.period))
        html = template.render(report=report)
        pdf_bytes: bytes = HTML(string=html, base_url=str(TEMPLATES_DIR)).write_pdf()
        return pdf_bytes
