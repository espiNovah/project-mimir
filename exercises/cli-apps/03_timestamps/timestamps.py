from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def parse_utc(text: str) -> datetime:
    """Parse an ISO 8601 string into an aware datetime in UTC. Naive strings raise ValueError."""
    raise NotImplementedError("Write this function")


def within_last(timestamps: list[str], now: datetime, days: int) -> list[str]:
    """Return the timestamps between `days` days before now and now (inclusive), in order."""
    raise NotImplementedError("Write this function")


def format_local(text: str, zone: str) -> str:
    """Show a timestamp on the clock of IANA time zone `zone`, as 'YYYY-MM-DD HH:MM'."""
    raise NotImplementedError("Write this function")
