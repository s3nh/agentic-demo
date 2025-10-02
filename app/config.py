from dataclasses import dataclass
from datetime import timedelta

@dataclass
class SLAConfig:
    default_ack_hours: int = 48
    high_severity_ack_hours: int = 24

@dataclass
class DraftingConfig:
    min_confidence: float = 0.65
    max_revision_rounds: int = 2

@dataclass
class RetrievalConfig:
    top_k: int = 5
    min_doc_confidence: float = 0.4

@dataclass
class RiskConfig:
    escalate_flags = {"THREAT_SELF_HARM", "THREAT_VIOLENCE"}
    hard_block_flags = set()

@dataclass
class OrchestratorConfig:
    sla: SLAConfig = SLAConfig()
    drafting: DraftingConfig = DraftingConfig()
    retrieval: RetrievalConfig = RetrievalConfig()
    risk: RiskConfig = RiskConfig()
    max_total_steps: int = 40
    enable_guardrails: bool = True

    def compute_sla_deadline(self, received_at, severity: str):
        hours = self.sla.default_ack_hours
        if severity in {"HIGH", "CRITICAL"}:
            hours = self.sla.high_severity_ack_hours
        return received_at + timedelta(hours=hours)
