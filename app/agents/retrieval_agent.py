from app.agents.base import BaseAgent
from app.models import ComplaintCase
from app.enums import CaseState

class RetrievalAgent(BaseAgent):
    def __init__(self):
        super().__init__("RetrievalAgent")

    def applicable(self, case: ComplaintCase) -> bool:
        return case.state == CaseState.ROUTING_PENDING and not case.retrieval_docs

    def run(self, step: int, case: ComplaintCase, tools):
        taxonomy_filter = [f for f in [case.product, case.issue] if f]
        docs = tools.retrieval.fetch_docs(taxonomy_filter, k=tools.config.retrieval.top_k)
        policies = tools.policy_store.get_clauses(case.product, case.issue)
        case.retrieval_docs = docs
        case.retrieval_policies = policies
        case.state = CaseState.DRAFTING
        case.log_event(step, self.name, "retrieval_done", {
            "doc_ids": [d["id"] for d in docs],
            "policy_ids": [p["id"] for p in policies]
        })
