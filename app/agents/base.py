from abc import ABC, abstractmethod
from typing import Protocol
from app.models import ComplaintCase

class ToolContext(Protocol):
    """Protocol for dependency container passed into agents."""
    ...

class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Agents receive a case and mutate it in-place.
    """

    name: str

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def applicable(self, case: ComplaintCase) -> bool:
        """Return True if this agent should run given the case state."""
        raise NotImplementedError

    @abstractmethod
    def run(self, step: int, case: ComplaintCase, tools: ToolContext):
        """Execute agent logic. Mutates case, logs events."""
        raise NotImplementedError
