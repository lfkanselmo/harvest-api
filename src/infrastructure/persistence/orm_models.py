from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class InternalMetricOrm(Base):
    __tablename__ = "internal_metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    value: Mapped[float]
    unit: Mapped[str]


class ReportOrm(Base):
    __tablename__ = "reports"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    generated_at: Mapped[datetime]
    period: Mapped[str]
    metrics_json: Mapped[str]
    pdf_path: Mapped[str]
