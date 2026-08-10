import pytest
from pydantic import ValidationError
from src.domain.value_objects import Metric, MetricStatus


def test_metric_ok_requires_a_value() -> None:
    with pytest.raises(ValidationError):
        Metric(name="temp_c", value=None, unit="°C", status=MetricStatus.OK)


def test_metric_unavailable_rejects_a_value() -> None:
    with pytest.raises(ValidationError):
        Metric(name="temp_c", value=22.5, unit="°C", status=MetricStatus.UNAVAILABLE)


def test_metric_ok_accepts_a_valid_value() -> None:
    metric = Metric(name="temp_c", value=22.5, unit="°C", status=MetricStatus.OK)

    assert metric.value == 22.5
    assert metric.status is MetricStatus.OK


def test_metric_unavailable_factory_has_no_value() -> None:
    metric = Metric.unavailable(name="WeatherAdapter", unit="°C")

    assert metric.name == "WeatherAdapter"
    assert metric.value is None
    assert metric.status is MetricStatus.UNAVAILABLE
