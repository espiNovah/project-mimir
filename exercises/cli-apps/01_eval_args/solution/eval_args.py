import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """Return the parser for `run-evals DATASET [--model {cheap,capable}] [--limit N] [--dry-run]`."""
    parser = argparse.ArgumentParser(prog="run-evals", description="Run an eval over a dataset.")
    parser.add_argument("dataset", type=Path, help="path to a JSONL file of test cases")
    parser.add_argument(
        "--model", choices=["cheap", "capable"], default="cheap", help="which model to evaluate"
    )
    parser.add_argument("--limit", type=int, default=50, help="run at most this many cases")
    parser.add_argument(
        "--dry-run", action="store_true", help="print what would run without calling the model"
    )
    return parser


def parse(argv: list[str]) -> argparse.Namespace:
    """Parse argv (a list of strings, without the program name)."""
    return build_parser().parse_args(argv)
