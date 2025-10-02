class RoutingEngine:
    def assign(self, case):
        if "POTENTIAL_FRAUD" in case.risk_flags:
            return {"queue": "FraudOps", "reason": "risk_flag_fraud", "requires_ack": True}
        if case.product == "DEBIT_CARD" and case.issue == "UNAUTHORIZED_TRANSACTION":
            return {"queue": "CardDisputes", "reason": "taxonomy_match", "requires_ack": True}
        if case.product == "ONLINE_BANKING":
            return {"queue": "DigitalSupport", "reason": "product_online_banking", "requires_ack": True}
        return {"queue": "GeneralSupport", "reason": "fallback", "requires_ack": True}
