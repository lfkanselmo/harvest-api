from pathlib import Path
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from src.application.ports.data_source import DataSource
from src.application.ports.notifier import Notifier
from src.application.ports.report_exporter import ReportExporter
from src.application.ports.report_repository import ReportRepository
from src.application.use_cases.generate_and_deliver_report import GenerateAndDeliverReportUseCase
from src.infrastructure.adapters.erp_adapter import ErpAdapter
from src.infrastructure.adapters.news_adapter import NewsAdapter
from src.infrastructure.adapters.weather_adapter import WeatherAdapter
from src.infrastructure.config import settings
from src.infrastructure.email.null_notifier import NullNotifier
from src.infrastructure.email.smtp_notifier import SmtpNotifier
from src.infrastructure.pdf.pdf_exporter import PDFExporter
from src.infrastructure.persistence.database import async_session_factory
from src.infrastructure.persistence.sqlite_report_repository import SqliteReportRepository


async def verify_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "API key invalida")


ApiKeyDep = Annotated[None, Depends(verify_api_key)]


def get_data_sources() -> list[DataSource]:
    return [
        WeatherAdapter(latitude=settings.weather_latitude, longitude=settings.weather_longitude),
        NewsAdapter(feed_url=settings.news_feed_url),
        ErpAdapter(async_session_factory),
    ]


def get_report_exporter() -> ReportExporter:
    return PDFExporter()


def get_report_repository() -> ReportRepository:
    return SqliteReportRepository(async_session_factory)


ReportRepoDep = Annotated[ReportRepository, Depends(get_report_repository)]


def get_notifier() -> Notifier:
    if settings.smtp_host is None:
        return NullNotifier()
    return SmtpNotifier(
        host=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        from_address=settings.smtp_from_address,
        use_tls=settings.smtp_use_tls,
        recipients=settings.report_recipients,
    )


def build_generate_and_deliver_use_case() -> GenerateAndDeliverReportUseCase:
    return GenerateAndDeliverReportUseCase(
        sources=get_data_sources(),
        exporter=get_report_exporter(),
        repository=get_report_repository(),
        notifier=get_notifier(),
        reports_dir=Path(settings.reports_dir),
    )


GenerateAndDeliverUseCaseDep = Annotated[
    GenerateAndDeliverReportUseCase, Depends(build_generate_and_deliver_use_case)
]
