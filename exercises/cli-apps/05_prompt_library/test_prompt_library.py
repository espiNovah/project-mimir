import json

import pytest

from prompt_library import main


@pytest.fixture
def lib(tmp_path):
    return tmp_path / "lib.json"


def run(lib, *argv):
    return main(["--file", str(lib), *argv])


def test_add_and_show(lib, capsys):
    assert run(lib, "add", "tutor", "You are a patient tutor.") == 0
    assert capsys.readouterr().out.strip() == "saved tutor"
    assert run(lib, "show", "tutor") == 0
    assert capsys.readouterr().out.strip() == "You are a patient tutor."


def test_file_is_json(lib):
    run(lib, "add", "tutor", "You are a patient tutor.")
    assert json.loads(lib.read_text(encoding="utf-8")) == {"tutor": "You are a patient tutor."}


def test_list_sorted(lib, capsys):
    run(lib, "add", "zeta", "z")
    run(lib, "add", "alpha", "a")
    capsys.readouterr()
    assert run(lib, "list") == 0
    assert capsys.readouterr().out.splitlines() == ["alpha", "zeta"]


def test_list_empty_when_no_file(lib, capsys):
    assert run(lib, "list") == 0
    assert capsys.readouterr().out == ""
    assert not lib.exists()


def test_duplicate_add_fails(lib, capsys):
    run(lib, "add", "tutor", "first")
    capsys.readouterr()
    assert run(lib, "add", "tutor", "second") == 1
    assert capsys.readouterr().err.strip() == "error: tutor already exists"
    assert json.loads(lib.read_text(encoding="utf-8")) == {"tutor": "first"}


def test_force_overwrites(lib):
    run(lib, "add", "tutor", "first")
    assert run(lib, "add", "tutor", "second", "--force") == 0
    assert json.loads(lib.read_text(encoding="utf-8")) == {"tutor": "second"}


def test_show_missing(lib, capsys):
    assert run(lib, "show", "nope") == 1
    out = capsys.readouterr()
    assert out.out == ""
    assert out.err.strip() == "error: no prompt named nope"


def test_no_subcommand_is_usage_error(lib):
    with pytest.raises(SystemExit) as exc:
        run(lib)
    assert exc.value.code == 2
