from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class InternalMetricOrm(Base):
    __tablename__ = "internal_metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    value: Mapped[float]
    unit: Mapped[str]
