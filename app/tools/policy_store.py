from typing import List, Dict

POLICY_DB = [
    {"id": "policy_refund_v4#clause2", "product": "DEBIT_CARD", "issue": "UNAUTHORIZED_TRANSACTION",
     "text": "Provisional credit typically within 10 business days.", "version": "2025.09"},
    {"id": "policy_disclaimer_general#ack", "product": None, "issue": None,
     "text": "This acknowledgment does not constitute a final decision.", "version": "2025.09"},
]

class PolicyStore:
    def get_clauses(self, product: str | None, issue: str | None) -> List[Dict]:
        results = []
        for rec in POLICY_DB:
            if rec["product"] is None and rec["issue"] is None:
                results.append(rec)
            elif rec["product"] == product and rec["issue"] == issue:
                results.append(rec)
        return results
