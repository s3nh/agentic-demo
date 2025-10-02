import argparse
import json
from app.models import ComplaintCase
from app.config import OrchestratorConfig
from app.orchestration.orchestrator import Orchestrator
from app.agents.normalization_agent import NormalizationAgent
from app.agents.classification_agent import ClassificationAgent
from app.agents.risk_agent import RiskScreeningAgent
from app.agents.routing_agent import RoutingAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.drafting_agent import DraftingAgent
from app.agents.qa_agent import QAAgent
from app.agents.hallucination_agent import HallucinationAgent
from app.agents.dispatch_agent import DispatchAgent
from app.agents.feedback_agent import FeedbackAgent
from app.tools.tool_context import ToolContext
from app.synthetic.generator import generate_cases
from app.enums import CaseState

def build_agents(config: OrchestratorConfig):
    return [
        NormalizationAgent(),
        ClassificationAgent(),
        RiskScreeningAgent(escalate_flags=config.risk.escalate_flags),
        RoutingAgent(),
        RetrievalAgent(),
        DraftingAgent(),
        QAAgent(max_revisions=config.drafting.max_revision_rounds, min_conf=config.drafting.min_confidence),
        HallucinationAgent(),
        DispatchAgent(),
        FeedbackAgent()
    ]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5, help="Number of synthetic complaints")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--output", type=str, default="")
    args = parser.parse_args()

    config = OrchestratorConfig()
    tools = ToolContext.build(config)
    agents = build_agents(config)
    orch = Orchestrator(config, agents)

    raw_cases = generate_cases(args.n)
    processed = []
    for c in raw_cases:
        case = ComplaintCase(case_id=c["case_id"], raw_text=c["raw_text"], channel=c["channel"], language=c["language"])
        final_case = orch.process_case(case, tools)
        processed.append(final_case)

        if args.verbose:
            print(f"Case {final_case.case_id} final state: {final_case.state.name}")
            if final_case.draft:
                print(" Draft excerpt:", final_case.draft.draft_text[:120], "...")
            print(" Events:")
            for ev in final_case.event_log:
                print(f"  - step={ev.step} agent={ev.agent} action={ev.action} state={ev.state_entered}")
            print("-" * 60)

    summary = {
        "total": len(processed),
        "sent": sum(1 for c in processed if c.state == CaseState.CLOSED and c.final_response_sent),
        "escalated": sum(1 for c in processed if any(e.agent == "RiskScreeningAgent" and 'escalated' in e.action for e in c.event_log)),
        "avg_draft_confidence": round(
            sum(c.draft.confidence for c in processed if c.draft) / max(1, sum(1 for c in processed if c.draft)), 3
        ),
    }
    print("\nSummary:", json.dumps(summary, indent=2))

    if args.output:
        serializable = []
        for c in processed:
            serializable.append({
                "case_id": c.case_id,
                "state": c.state.name,
                "product": c.product,
                "issue": c.issue,
                "risk_flags": c.risk_flags,
                "routing_queue": c.routing_queue,
                "draft_confidence": c.draft.confidence if c.draft else None
            })
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2)

if __name__ == "__main__":
    main()
