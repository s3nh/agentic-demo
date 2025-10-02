from app.agents.base import BaseAgent
from app.models import ComplaintCase, DraftObject
from app.enums import CaseState

class DraftingAgent(BaseAgent):
    def __init__(self):
        super().__init__("DraftingAgent")

    def applicable(self, case: ComplaintCase) -> bool:
        return case.state == CaseState.DRAFTING and case.draft is None

    def run(self, step: int, case: ComplaintCase, tools):
        prompt = tools.drafting_llm.build_prompt(case)
        draft_json = tools.drafting_llm.generate(prompt)
        draft = DraftObject(
            draft_text=draft_json["draft_response"],
            citations=draft_json["citations"],
            disclaimers=draft_json["disclaimers"],
            recommended_actions=draft_json["recommended_actions"],
            tone=draft_json["tone"],
            confidence=draft_json["confidence"]
        )
        case.draft = draft
        case.state = CaseState.QA_REVIEW
        case.log_event(step, self.name, "draft_created", {
            "confidence": draft.confidence,
            "citations": draft.citations
        })
