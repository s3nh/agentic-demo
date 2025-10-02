from typing import List, Dict
import random

KB_ARTICLES = [
    {"id": "kb_debit_unauth_112", "taxonomy": ["DEBIT_CARD", "UNAUTHORIZED_TRANSACTION"],
     "summary": "Steps for unauthorized debit transactions & dispute timeline."},
    {"id": "kb_lockout_44", "taxonomy": ["ONLINE_BANKING", "ACCESS_LOCKOUT"],
     "summary": "Guidance on multi-factor resets and identity verification."},
    {"id": "kb_fees_disc_31", "taxonomy": ["CREDIT_CARD", "FEES_DISCLOSURE"],
     "summary": "Regulations on fee disclosure and statement layout."},
]

class RetrievalClient:
    def fetch_docs(self, taxonomy_filters: List[str], k: int = 5) -> List[Dict]:
        # Simple filter subset + random ranking
        candidates = []
        for doc in KB_ARTICLES:
            if any(t in doc["taxonomy"] for t in taxonomy_filters):
                candidates.append(doc)
        if not candidates:
            candidates = KB_ARTICLES[:]  # fallback
        random.shuffle(candidates)
        return candidates[:k]
