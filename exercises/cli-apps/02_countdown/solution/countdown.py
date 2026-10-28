import argparse
import sys
from datetime import date


def days_between(start: date, end: date) -> int:
    """Return the number of days from start to end (negative if end is earlier)."""
    return (end - start).days


def main(argv: list[str] | None = None) -> int:
    """Parse argv, print the countdown, and return an exit code (0 ok, 1 date in the past)."""
    parser = argparse.ArgumentParser(prog="countdown", description="Count the days until a date.")
    parser.add_argument("target", type=date.fromisoformat, help="the date, as YYYY-MM-DD")
    parser.add_argument(
        "--since", type=date.fromisoformat, default=date.today(), help="count from this date"
    )
    parser.add_argument("--weeks", action="store_true", help="show weeks and days")
    args = parser.parse_args(argv)

    days = days_between(args.since, args.target)
    if days < 0:
        print(f"error: {args.target} is in the past", file=sys.stderr)
        return 1
    if args.weeks:
        print(f"{days // 7} weeks and {days % 7} days until {args.target}")
    else:
        print(f"{days} days until {args.target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
