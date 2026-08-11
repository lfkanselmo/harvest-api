from abc import ABC, abstractmethod
from typing import ClassVar

from src.domain.value_objects import Metric


class DataSource(ABC):
    source_name: ClassVar[str] = "fuente desconocida"

    @abstractmethod
    async def fetch(self) -> list[Metric]: ...
