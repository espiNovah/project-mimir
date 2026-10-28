from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def parse_utc(text: str) -> datetime:
    """Parse an ISO 8601 string into an aware datetime in UTC. Naive strings raise ValueError."""
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"timestamp has no time zone: {text!r}")
    return dt.astimezone(timezone.utc)


def within_last(timestamps: list[str], now: datetime, days: int) -> list[str]:
    """Return the timestamps between `days` days before now and now (inclusive), in order."""
    cutoff = now - timedelta(days=days)
    return [t for t in timestamps if cutoff <= parse_utc(t) <= now]


def format_local(text: str, zone: str) -> str:
    """Show a timestamp on the clock of IANA time zone `zone`, as 'YYYY-MM-DD HH:MM'."""
    return parse_utc(text).astimezone(ZoneInfo(zone)).strftime("%Y-%m-%d %H:%M")
