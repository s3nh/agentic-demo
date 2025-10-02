class HallucinationCheck:
    """
    Simple stub: increases score if numeric timelines with no citation appear.
    """
    def score(self, case):
        if not case.draft:
            return 1.0
        text = case.draft.draft_text
        score = 0.0
        if "business days" in text and not case.draft.citations:
            score += 0.3
        if "guarantee" in text.lower():
            score += 0.4
        return min(score, 1.0)
