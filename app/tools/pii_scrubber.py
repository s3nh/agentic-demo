import re
from typing import Tuple, Dict

class PIIScrubber:
    EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    PHONE_RE = re.compile(r"\b\d{3}[- ]?\d{3}[- ]?\d{4}\b", re.IGNORECASE)
    NAME_LIST = {"john", "jane", "robert"}  # simplistic placeholder

    def scrub(self, text: str) -> Tuple[str, Dict[str, str]]:
        redactions = {}
        def _sub(pattern, placeholder_prefix):
            nonlocal text
            matches = list(pattern.finditer(text))
            for i, m in enumerate(matches, start=1):
                original = m.group(0)
                placeholder = f"<{placeholder_prefix}_{i}>"
                redactions[original] = placeholder
                text = text.replace(original, placeholder)
        _sub(self.EMAIL_RE, "EMAIL")
        _sub(self.PHONE_RE, "PHONE")

        # Naive name handling
        tokens = text.split()
        for i, t in enumerate(tokens):
            if t.lower().strip(",.") in self.NAME_LIST:
                placeholder = f"<PERSON_{i}>"
                redactions[t] = placeholder
                tokens[i] = placeholder
        text = " ".join(tokens)
        return text, redactions
