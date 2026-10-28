import re

US_DATE_RE = re.compile(r"\b(?P<month>\d{2})/(?P<day>\d{2})/(?P<year>\d{4})\b")
ISO_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def us_to_iso(text: str) -> str:
    """Rewrite every MM/DD/YYYY date in text as YYYY-MM-DD."""
    return US_DATE_RE.sub(r"\g<year>-\g<month>-\g<day>", text)


def find_dates(text: str) -> list[str]:
    """Return every date in text (ISO or US style) as ISO strings, in order."""
    return ISO_DATE_RE.findall(us_to_iso(text))
