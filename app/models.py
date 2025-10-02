
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.enums import CaseState

@dataclass
class EventLog:
    step: int
    agent: str
    action: str
    state_entered: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class DraftObject:
    draft_text: str
    citations: List[str]
    disclaimers: List[str]
    recommended_actions: List[str]
    tone: str
    confidence: float

@dataclass
class ComplaintCase:
    case_id: str
    raw_text: str
    channel: str
    language: str = "en"
    normalized_text: Optional[str] = None
    product: Optional[str] = None
    issue: Optional[str] = None
    sub_issue: Optional[str] = None
    severity: Optional[str] = None
    risk_flags: List[str] = field(default_factory=list)
    vulnerability_flag: bool = False
    routing_queue: Optional[str] = None
    policy_version_pin: Optional[str] = None
    sla_deadline: Optional[datetime] = None
    draft: Optional[DraftObject] = None
    qa_approved: bool = False
    final_response_sent: bool = False
    state: CaseState = CaseState.RECEIVED
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    event_log: List[EventLog] = field(default_factory=list)
    retrieval_docs: List[Dict[str, Any]] = field(default_factory=list)
    retrieval_policies: List[Dict[str, Any]] = field(default_factory=list)
    revision_rounds: int = 0
    classification_confidence: float = 0.0
    routing_reason: Optional[str] = None
    hallucination_score: float = 0.0
    errors: List[str] = field(default_factory=list)

    def log_event(self, step: int, agent: str, action: str, payload: Dict[str, Any]):
        self.event_log.append(
            EventLog(step=step, agent=agent, action=action,
                     state_entered=self.state.name, payload=payload)
        )
        self.updated_at = datetime.utcnow()
