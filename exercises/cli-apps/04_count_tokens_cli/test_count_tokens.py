import pytest

from count_tokens import estimate_tokens, main


@pytest.fixture
def files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # so the tests can use short relative names
    (tmp_path / "notes.md").write_text("a" * 50, encoding="utf-8")  # 13 tokens at 4/token
    (tmp_path / "prompt.txt").write_text("b" * 8, encoding="utf-8")  # 2 tokens
    return tmp_path


def test_estimate_tokens():
    assert estimate_tokens("abcde") == 2
    assert estimate_tokens("") == 0
    assert estimate_tokens("abcdef", chars_per_token=3) == 2


def test_one_file(files, capsys):
    assert main(["notes.md"]) == 0
    assert capsys.readouterr().out.splitlines() == ["notes.md: 13 tokens", "total: 13 tokens"]


def test_two_files_and_total(files, capsys):
    assert main(["notes.md", "prompt.txt"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "notes.md: 13 tokens",
        "prompt.txt: 2 tokens",
        "total: 15 tokens",
    ]


def test_chars_per_token(files, capsys):
    assert main(["prompt.txt", "--chars-per-token", "3"]) == 0
    assert capsys.readouterr().out.splitlines() == ["prompt.txt: 3 tokens", "total: 3 tokens"]


def test_missing_file_is_reported_and_skipped(files, capsys):
    assert main(["notes.md", "missing.txt", "prompt.txt"]) == 1
    out = capsys.readouterr()
    assert out.out.splitlines() == [
        "notes.md: 13 tokens",
        "prompt.txt: 2 tokens",
        "total: 15 tokens",
    ]
    assert out.err.strip() == "error: no such file: missing.txt"


def test_no_files_is_usage_error(files):
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2
