import re

_SPAM_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"download\s+free",
        r"click\s+here",
        r"earn\s+money",
        r"whatsapp",
        r"telegram\.me",
        r"bit\.ly",
    ]
]


def is_spam(text: str | None, rating: int | None = None) -> bool:
    if not text or not text.strip():
        return False
    if len(text.strip()) < 3 and rating is not None:
        return False
    lowered = text.lower()
    if any(p.search(lowered) for p in _SPAM_PATTERNS):
        return True
    # Very short all-caps bursts
    if len(text) < 20 and text.isupper() and " " not in text:
        return True
    return False
