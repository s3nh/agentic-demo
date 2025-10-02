from app.agents.base import BaseAgent
from app.models import ComplaintCase
from app.enums import CaseState

class HallucinationAgent(BaseAgent):
    def __init__(self, threshold: float = 0.25):
        super().__init__("HallucinationAgent")
        self.threshold = threshold

    def applicable(self, case: ComplaintCase) -> bool:
        return case.state == CaseState.READY_TO_SEND and case.draft is not None

    def run(self, step: int, case: ComplaintCase, tools):
        score = tools.hallucination_check.score(case)
        case.hallucination_score = score
        if score > self.threshold:
            # Replace with safe fallback
            safe_draft = tools.drafting_llm.safe_fallback(case)
            case.draft.draft_text = safe_draft["draft_response"]
            case.draft.citations = safe_draft["citations"]
            case.draft.disclaimers = safe_draft["disclaimers"]
            case.log_event(step, self.name, "fallback_applied", {"score": score})
        else:
            case.log_event(step, self.name, "hallucination_pass", {"score": score})
