import re


def us_to_iso(text: str) -> str:
    """Rewrite every MM/DD/YYYY date in text as YYYY-MM-DD."""
    raise NotImplementedError("Write this function")


def find_dates(text: str) -> list[str]:
    """Return every date in text (ISO or US style) as ISO strings, in order."""
    raise NotImplementedError("Write this function")
