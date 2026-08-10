from abc import ABC, abstractmethod

from src.domain.value_objects import Metric


class DataSource(ABC):
    @abstractmethod
    async def fetch(self) -> list[Metric]: ...
