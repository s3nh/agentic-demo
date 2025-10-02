class QAGuardrail:
    def validate(self, case):
        issues = []
        if case.draft is None:
            return {"approved": False, "issues": ["missing_draft"]}

        text = case.draft.draft_text.lower()
        # Mandatory disclaimer check if dispute-like issue
        if case.issue == "UNAUTHORIZED_TRANSACTION":
            has_disc = any("acknowledgment does not constitute" in d.lower() for d in case.draft.disclaimers)
            if not has_disc:
                issues.append("missing_disclaimer")

        # Banned phrase example
        if "guarantee full refund" in text:
            issues.append("banned_phrase_guarantee_refund")

        # Citation requirement if referencing timeline
        if "within 10 business days" in text and not any("policy_refund_v4#clause2" in c for c in case.draft.citations):
            issues.append("missing_citation_for_timeline")

        approved = not issues and case.draft.confidence >= 0.65
        return {
            "approved": approved,
            "issues": issues,
            "confidence": case.draft.confidence
        }
