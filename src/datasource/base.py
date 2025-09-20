from abc import ABC, abstractmethod
from typing import Any, Dict, List

class DataSource(ABC):
    @abstractmethod
    async def fetch(self, asset: str, **kwargs) -> Dict[str, Any]:
        ...
