import random

class RiskDetector:
    def scan(self, text: str):
        flags = []
        lower = text.lower()
        if any(k in lower for k in ["kill myself", "end my life", "suicide"]):
            flags.append("THREAT_SELF_HARM")
        if "threat" in lower or "violence" in lower:
            flags.append("THREAT_VIOLENCE")
        if "fraud" in lower or "scam" in lower or "identity theft" in lower:
            flags.append("POTENTIAL_FRAUD")
        vulnerability_flag = any(word in lower for word in ["disability", "elderly"])
        # Random mild risk noise
        if random.random() < 0.05:
            flags.append("POTENTIAL_AML")
        return {
            "risk_flags": list(set(flags)),
            "vulnerability_flag": vulnerability_flag,
            "confidence": 0.9 if flags else 0.7
        }
