from app.agents.base import BaseAgent
from app.models import ComplaintCase
from app.enums import CaseState

class DispatchAgent(BaseAgent):
    def __init__(self):
        super().__init__("DispatchAgent")

    def applicable(self, case: ComplaintCase) -> bool:
        return case.state == CaseState.READY_TO_SEND and case.draft is not None and not case.final_response_sent

    def run(self, step: int, case: ComplaintCase, tools):
        tools.dispatcher.send(case)
        case.final_response_sent = True
        case.state = CaseState.SENT
        case.log_event(step, self.name, "dispatched", {
            "queue": case.routing_queue,
            "length": len(case.draft.draft_text)
        })
