from pathlib import Path

import pytest

from eval_args import build_parser, parse


def test_defaults():
    args = parse(["golden.jsonl"])
    assert args.dataset == Path("golden.jsonl")
    assert isinstance(args.dataset, Path)
    assert args.model == "cheap"
    assert args.limit == 50
    assert args.dry_run is False


def test_all_options():
    args = parse(["golden.jsonl", "--model", "capable", "--limit", "10", "--dry-run"])
    assert args.model == "capable"
    assert args.limit == 10
    assert args.dry_run is True


def test_options_before_positional():
    args = parse(["--limit", "5", "data/test.jsonl"])
    assert args.dataset == Path("data/test.jsonl")
    assert args.limit == 5


@pytest.mark.parametrize(
    "argv",
    [
        [],  # dataset is required
        ["golden.jsonl", "--model", "huge"],
        ["golden.jsonl", "--limit", "ten"],
        ["golden.jsonl", "--wat"],
    ],
)
def test_usage_errors_exit_2(argv, capsys):
    with pytest.raises(SystemExit) as exc:
        parse(argv)
    assert exc.value.code == 2
    assert "usage: run-evals" in capsys.readouterr().err


def test_help_mentions_every_argument():
    text = build_parser().format_help()
    for name in ["dataset", "--model", "--limit", "--dry-run"]:
        assert name in text
