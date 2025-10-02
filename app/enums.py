from enum import Enum, auto

class CaseState(Enum):
    RECEIVED = auto()
    NORMALIZED = auto()
    CLASSIFIED = auto()
    RISK_SCREENED = auto()
    ROUTING_PENDING = auto()
    DRAFTING = auto()
    QA_REVIEW = auto()
    READY_TO_SEND = auto()
    SENT = auto()
    ESCALATED = auto()
    CLOSED = auto()
    ERROR = auto()
