from typing import List
from app.models import ComplaintCase
from app.enums import CaseState
from app.config import OrchestratorConfig

class Orchestrator:
    """
    Orchestrates agent execution in deterministic passes.
    Each loop iteration increments a 'step' counter.
    """
    def __init__(self, config: OrchestratorConfig, agents: List):
        self.config = config
        self.agents = agents

    def process_case(self, case: ComplaintCase, tools) -> ComplaintCase:
        step = 0
        while step < self.config.max_total_steps:
            step += 1
            progressed = False
            # Determine SLA (once severity known and not yet set)
            if case.state == CaseState.CLASSIFIED and not case.sla_deadline:
                case.sla_deadline = self.config.compute_sla_deadline(case.created_at, case.severity or "LOW")
            for agent in self.agents:
                if agent.applicable(case):
                    agent.run(step, case, tools)
                    progressed = True
                    if case.state in {CaseState.CLOSED, CaseState.ERROR}:
                        return case
            # Terminal conditions
            if case.state in {CaseState.SENT, CaseState.ESCALATED}:
                # Allow feedback agent to close
                continue
            if not progressed:
                # No agent acted; break to avoid infinite loop
                break
        return case
