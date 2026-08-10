from enum import StrEnum

from pydantic import BaseModel, ConfigDict, model_validator


class MetricStatus(StrEnum):
    OK = "ok"
    UNAVAILABLE = "unavailable"


class Metric(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    value: float | None
    unit: str
    status: MetricStatus

    @model_validator(mode="after")
    def _value_matches_status(self) -> "Metric":
        if self.status is MetricStatus.OK and self.value is None:
            raise ValueError("una metrica con status 'ok' requiere un value")
        if self.status is MetricStatus.UNAVAILABLE and self.value is not None:
            raise ValueError("una metrica con status 'unavailable' no debe tener value")
        return self

    @classmethod
    def unavailable(cls, name: str, unit: str = "") -> "Metric":
        return cls(name=name, value=None, unit=unit, status=MetricStatus.UNAVAILABLE)
