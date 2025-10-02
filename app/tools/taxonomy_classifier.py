import random

PRODUCTS = ["DEBIT_CARD", "CREDIT_CARD", "MORTGAGE", "ONLINE_BANKING"]
ISSUES = ["UNAUTHORIZED_TRANSACTION", "ACCESS_LOCKOUT", "FEES_DISCLOSURE", "PAYMENT_PROCESSING_DELAY"]
SUB_ISSUES = {
    "UNAUTHORIZED_TRANSACTION": ["CARD_NOT_PRESENT", "LOST_STOLEN_CARD", "PHISHING_RESULT"],
    "ACCESS_LOCKOUT": ["PASSWORD_RESET_FAILURE", "2FA_ISSUE"]
}

class TaxonomyClassifier:
    """
    Stub classifier that uses keyword heuristics.
    Replace with real ML model integration.
    """
    def classify(self, text: str):
        lower = text.lower()
        product = random.choice(PRODUCTS)
        issue = "UNAUTHORIZED_TRANSACTION" if "unauthorized" in lower or "not mine" in lower else random.choice(ISSUES)
        if issue in SUB_ISSUES:
            sub_issue = random.choice(SUB_ISSUES[issue])
        else:
            sub_issue = None
        severity = "HIGH" if "fraud" in lower or "stolen" in lower else random.choice(["LOW", "MED"])
        confidence = round(random.uniform(0.6, 0.95), 2)
        return {
            "product": product,
            "issue": issue,
            "sub_issue": sub_issue,
            "severity": severity,
            "confidence": confidence,
            "needs_human": confidence < 0.6
        }
