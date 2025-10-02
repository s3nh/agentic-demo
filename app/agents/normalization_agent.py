from app.agents.base import BaseAgent
from app.models import ComplaintCase
from app.enums import CaseState

class NormalizationAgent(BaseAgent):
    def __init__(self):
        super().__init__("NormalizationAgent")

    def applicable(self, case: ComplaintCase) -> bool:
        return case.state == CaseState.RECEIVED

    def run(self, step: int, case: ComplaintCase, tools):
        normalized, redactions = tools.pii_scrubber.scrub(case.raw_text)
        case.normalized_text = normalized
        case.state = CaseState.NORMALIZED
        case.log_event(step, self.name, "redact+normalize", {
            "redactions": redactions,
            "length_before": len(case.raw_text),
            "length_after": len(normalized)
        })
