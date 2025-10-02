from dataclasses import dataclass
from app.config import OrchestratorConfig
from app.tools.pii_scrubber import PIIScrubber
from app.tools.taxonomy_classifier import TaxonomyClassifier
from app.tools.risk_detector import RiskDetector
from app.tools.policy_store import PolicyStore
from app.tools.retrieval import RetrievalClient
from app.tools.drafting_llm import DraftingLLM
from app.tools.qa_guardrail import QAGuardrail
from app.tools.hallucination_check import HallucinationCheck
from app.tools.routing_engine import RoutingEngine
from app.tools.dispatcher import Dispatcher
from app.tools.feedback_collector import FeedbackCollector

@dataclass
class ToolContext:
    config: OrchestratorConfig
    pii_scrubber: PIIScrubber
    taxonomy_classifier: TaxonomyClassifier
    risk_detector: RiskDetector
    policy_store: PolicyStore
    retrieval: RetrievalClient
    drafting_llm: DraftingLLM
    qa_guardrail: QAGuardrail
    hallucination_check: HallucinationCheck
    routing_engine: RoutingEngine
    dispatcher: Dispatcher
    feedback_collector: FeedbackCollector

    @classmethod
    def build(cls, config: OrchestratorConfig):
        return cls(
            config=config,
            pii_scrubber=PIIScrubber(),
            taxonomy_classifier=TaxonomyClassifier(),
            risk_detector=RiskDetector(),
            policy_store=PolicyStore(),
            retrieval=RetrievalClient(),
            drafting_llm=DraftingLLM(),
            qa_guardrail=QAGuardrail(),
            hallucination_check=HallucinationCheck(),
            routing_engine=RoutingEngine(),
            dispatcher=Dispatcher(),
            feedback_collector=FeedbackCollector()
        )
