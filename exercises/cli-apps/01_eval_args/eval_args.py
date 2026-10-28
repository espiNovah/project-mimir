import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """Return the parser for `run-evals DATASET [--model {cheap,capable}] [--limit N] [--dry-run]`."""
    raise NotImplementedError("Write this function")


def parse(argv: list[str]) -> argparse.Namespace:
    """Parse argv (a list of strings, without the program name)."""
    return build_parser().parse_args(argv)
