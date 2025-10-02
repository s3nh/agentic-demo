from app.agents.base import BaseAgent
from app.models import ComplaintCase
from app.enums import CaseState

class ClassificationAgent(BaseAgent):
    def __init__(self, min_conf: float = 0.55):
        super().__init__("ClassificationAgent")
        self.min_conf = min_conf

    def applicable(self, case: ComplaintCase) -> bool:
        return case.state == CaseState.NORMALIZED

    def run(self, step: int, case: ComplaintCase, tools):
        result = tools.taxonomy_classifier.classify(case.normalized_text or "")
        case.product = result["product"]
        case.issue = result["issue"]
        case.sub_issue = result.get("sub_issue")
        case.severity = result["severity"]
        case.classification_confidence = result["confidence"]
        if result.get("needs_human"):
            case.state = CaseState.ESCALATED
            case.log_event(step, self.name, "classification_escalated", result)
            return
        case.state = CaseState.CLASSIFIED
        case.log_event(step, self.name, "classified", result)
