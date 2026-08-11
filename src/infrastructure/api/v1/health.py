from fastapi import APIRouter

from src.application.use_cases.check_sources_health import CheckSourcesHealthUseCase
from src.infrastructure.api.dependencies import DataSourcesDep
from src.infrastructure.api.v1.schemas import SourceHealthOut

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/sources")
async def sources_health(sources: DataSourcesDep) -> list[SourceHealthOut]:
    results = await CheckSourcesHealthUseCase(sources).execute()
    return [SourceHealthOut.from_domain(result) for result in results]
