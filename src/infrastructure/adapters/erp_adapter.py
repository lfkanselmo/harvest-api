import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.ports.data_source import DataSource
from src.domain.value_objects import Metric, MetricStatus
from src.infrastructure.persistence.orm_models import InternalMetricOrm

logger = logging.getLogger(__name__)


class ErpAdapter(DataSource):
    source_name = "Métricas internas"

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def fetch(self) -> list[Metric]:
        try:
            async with self._session_factory() as session:
                rows = (await session.execute(select(InternalMetricOrm))).scalars().all()
        except SQLAlchemyError:
            logger.warning("ErpAdapter no pudo leer internal_metrics", exc_info=True)
            return [Metric.unavailable(name=self.source_name)]

        if not rows:
            return [Metric.unavailable(name=self.source_name)]

        return [
            Metric(name=row.name, value=row.value, unit=row.unit, status=MetricStatus.OK)
            for row in rows
        ]
