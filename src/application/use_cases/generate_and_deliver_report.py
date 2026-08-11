import logging
from pathlib import Path

from src.application.ports.data_source import DataSource
from src.application.ports.notifier import Notifier
from src.application.ports.report_exporter import ReportExporter
from src.application.ports.report_repository import ReportRepository
from src.application.use_cases.generate_report import GenerateReportUseCase
from src.domain.models import Report, ReportPeriod

logger = logging.getLogger(__name__)


class GenerateAndDeliverReportUseCase:
    def __init__(
        self,
        sources: list[DataSource],
        exporter: ReportExporter,
        repository: ReportRepository,
        notifier: Notifier,
        reports_dir: Path,
    ) -> None:
        self._sources = sources
        self._exporter = exporter
        self._repository = repository
        self._notifier = notifier
        self._reports_dir = reports_dir

    async def execute(self, period: ReportPeriod = ReportPeriod.DAILY) -> Report:
        report = await GenerateReportUseCase().execute(self._sources, period)
        pdf_bytes = self._exporter.export(report)

        self._reports_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = self._reports_dir / f"{report.id}.pdf"
        pdf_path.write_bytes(pdf_bytes)

        await self._repository.save(report, pdf_path)

        try:
            await self._notifier.send(report, pdf_bytes)
        except Exception:
            logger.error("No se pudo enviar el informe %s por correo", report.id, exc_info=True)

        return report
