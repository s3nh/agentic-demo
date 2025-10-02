"""
Drafting LLM stub.
Replace generate() with real model API calls.
"""
from typing import Dict, List
import random

class DraftingLLM:
    def build_prompt(self, case) -> str:
        return f"""
SYSTEM: You are a banking complaint drafting assistant.
PRODUCT: {case.product} ISSUE: {case.issue} SUB_ISSUE: {case.sub_issue}
RISK_FLAGS: {case.risk_flags}
POLICIES: {[p['id'] for p in case.retrieval_policies]}
DOCS: {[d['id'] for d in case.retrieval_docs]}
USER_COMPLAINT:
{case.normalized_text}
Respond in JSON with fields: draft_response, citations, disclaimers, recommended_actions, tone, confidence.
"""

    def generate(self, prompt: str) -> Dict:
        # Heuristic synthetic generation
        disclaimers = []
        if "UNAUTHORIZED_TRANSACTION" in prompt:
            disclaimers.append("This acknowledgment does not constitute a final decision.")
        citations = ["policy_refund_v4#clause2"] if "policy_refund_v4#clause2" in prompt else []
        citations += ["kb_debit_unauth_112"] if "kb_debit_unauth_112" in prompt else []
        resp = {
            "draft_response": "Hello, we have received your report regarding the transaction. "
                              "We are reviewing it and may request supporting documents.",
            "citations": list(set(citations)),
            "disclaimers": disclaimers,
            "recommended_actions": ["Provide transaction date verification"],
            "tone": "empathetic_professional",
            "confidence": round(random.uniform(0.66, 0.9), 2)
        }
        return resp

    def revise(self, case, qa_report: Dict) -> Dict:
        # Simple improvement: append clarifications for each issue
        improved = {
            "draft_response": case.draft.draft_text + " " +
                              " ".join(f"Addressing: {i}" for i in qa_report["issues"])[:400],
            "citations": case.draft.citations,
            "disclaimers": list(set(case.draft.disclaimers)),
            "recommended_actions": case.draft.recommended_actions,
            "tone": case.draft.tone,
            "confidence": min(0.95, case.draft.confidence + 0.05)
        }
        return improved

    def safe_fallback(self, case) -> Dict:
        return {
            "draft_response": "We acknowledge receipt of your complaint. "
                              "Additional review is required before we can provide further details.",
            "citations": [],
            "disclaimers": ["This acknowledgment does not constitute a final decision."],
            "recommended_actions": [],
            "tone": "neutral",
            "confidence": 0.55
        }
