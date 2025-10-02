from app.agents.base import BaseAgent
from app.models import ComplaintCase
from app.enums import CaseState

class FeedbackAgent(BaseAgent):
    """
    Runs after SENT (or ESCALATED) to record metrics and finalize.
    """

    def __init__(self):
        super().__init__("FeedbackAgent")

    def applicable(self, case: ComplaintCase) -> bool:
        return case.state in {CaseState.SENT, CaseState.ESCALATED} and case.state != CaseState.CLOSED

    def run(self, step: int, case: ComplaintCase, tools):
        tools.feedback_collector.record(case)
        case.state = CaseState.CLOSED
        case.log_event(step, self.name, "case_closed", {"status": case.state.name})
