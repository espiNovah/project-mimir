import argparse
import sys
from datetime import date


def days_between(start: date, end: date) -> int:
    """Return the number of days from start to end (negative if end is earlier)."""
    raise NotImplementedError("Write this function")


def main(argv: list[str] | None = None) -> int:
    """Parse argv, print the countdown, and return an exit code (0 ok, 1 date in the past)."""
    raise NotImplementedError("Write this function")


if __name__ == "__main__":
    sys.exit(main())
