import re

ANSWER_RE = re.compile(r"answer\W*([A-D])\b", re.IGNORECASE)


def extract_choice(reply: str) -> str | None:
    """Return the letter (A-D) after the last 'answer' in reply, uppercased, or None."""
    matches = ANSWER_RE.findall(reply)
    if not matches:
        return None
    return matches[-1].upper()  # models sometimes restate; trust the last one
