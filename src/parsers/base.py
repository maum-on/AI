from abc import ABC, abstractmethod
from typing import Any
from src.schemas.chat import ChatThread

class BaseChatParser(ABC):
    @abstractmethod
    def can_handle(self, payload: Any) -> bool: ...

    @abstractmethod
    def parse(self, payload: Any, me_hint: str | None = None) -> ChatThread: ...
