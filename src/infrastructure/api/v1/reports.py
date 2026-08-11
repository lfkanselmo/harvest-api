from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from src.infrastructure.api.dependencies import (
    ApiKeyDep,
    GenerateAndDeliverUseCaseDep,
    ReportRepoDep,
)
from src.infrastructure.api.v1.schemas import ReportOut

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate", response_model=ReportOut)
async def generate_report(use_case: GenerateAndDeliverUseCaseDep, _: ApiKeyDep) -> ReportOut:
    report = await use_case.execute()
    return ReportOut.from_domain(report)


@router.get("", response_model=list[ReportOut])
async def list_reports(
    repository: ReportRepoDep, _: ApiKeyDep, limit: int = 20
) -> list[ReportOut]:
    reports = await repository.list_recent(limit)
    return [ReportOut.from_domain(report) for report in reports]


@router.get("/{report_id}/download")
async def download_report(
    report_id: UUID, repository: ReportRepoDep, _: ApiKeyDep
) -> FileResponse:
    pdf_path = await repository.get_pdf_path(report_id)
    if pdf_path is None or not pdf_path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reporte no encontrado")
    return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_path.name)
