from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseEnterpriseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        pass
