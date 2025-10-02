from app.agents.base import BaseAgent
from app.models import ComplaintCase
from app.enums import CaseState

class RoutingAgent(BaseAgent):
    def __init__(self):
        super().__init__("RoutingAgent")

    def applicable(self, case: ComplaintCase) -> bool:
        return case.state == CaseState.RISK_SCREENED

    def run(self, step: int, case: ComplaintCase, tools):
        route = tools.routing_engine.assign(case)
        case.routing_queue = route["queue"]
        case.routing_reason = route["reason"]
        # Decide if drafting is needed (e.g., initial acknowledgment)
        if route["requires_ack"]:
            case.state = CaseState.ROUTING_PENDING
        else:
            case.state = CaseState.READY_TO_SEND
        case.log_event(step, self.name, "routing_decision", route)
