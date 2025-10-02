import random
from typing import List, Dict

BASE_TEXTS = [
    "I see an unauthorized charge on my debit card that I did not make yesterday.",
    "Locked out of my online banking account after multiple password attempts.",
    "I was charged a fee I was not told about on my credit card.",
    "Payment processing delay caused my mortgage payment to show late.",
    "Potential fraud noticed in my recent transactions, please help."
]

def generate_cases(n: int) -> List[Dict]:
    data = []
    for i in range(n):
        base = random.choice(BASE_TEXTS)
        noise = "" if random.random() < 0.7 else " There were also other strange activities."
        text = base + noise
        data.append({
            "case_id": f"C_SYN_{i:04d}",
            "raw_text": text,
            "channel": random.choice(["web_form", "email", "chat"]),
            "language": "en"
        })
    return data
