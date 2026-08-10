import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from src.domain.value_objects import MetricStatus
from src.infrastructure.adapters.erp_adapter import ErpAdapter
from src.infrastructure.persistence.orm_models import Base, InternalMetricOrm

pytestmark = pytest.mark.integration


async def _session_factory(seed: bool) -> async_sessionmaker:  # type: ignore[type-arg]
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    if seed:
        async with factory() as session:
            session.add(InternalMetricOrm(name="active_users", value=100.0, unit="usuarios"))
            await session.commit()
    return factory


async def test_fetch_returns_seeded_metrics() -> None:
    adapter = ErpAdapter(await _session_factory(seed=True))

    metrics = await adapter.fetch()

    assert metrics[0].name == "active_users"
    assert metrics[0].value == 100.0
    assert metrics[0].status is MetricStatus.OK


async def test_fetch_degrades_when_table_is_empty() -> None:
    adapter = ErpAdapter(await _session_factory(seed=False))

    metrics = await adapter.fetch()

    assert metrics[0].status is MetricStatus.UNAVAILABLE
