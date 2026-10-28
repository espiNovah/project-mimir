from prompt_builder import build_prompt, call_with_defaults


def test_joins_parts():
    assert build_prompt("You are helpful.", "Answer briefly.") == "You are helpful.\n\nAnswer briefly."


def test_skips_empty_parts():
    assert build_prompt("A", "", "B") == "A\n\nB"


def test_custom_separator():
    assert build_prompt("A", "B", sep=" | ") == "A | B"


def test_fills_variables():
    assert build_prompt("Hello {name}.", "Topic: {topic}", name="Ada", topic="evals") == (
        "Hello Ada.\n\nTopic: evals"
    )


def test_no_parts():
    assert build_prompt() == ""


def fake_model(prompt, *, temperature, max_tokens=100):
    return (prompt, temperature, max_tokens)


def test_call_with_defaults_adds_temperature():
    assert call_with_defaults(fake_model, "hi") == ("hi", 0.0, 100)


def test_call_with_defaults_keeps_caller_values():
    assert call_with_defaults(fake_model, "hi", temperature=0.7, max_tokens=5) == ("hi", 0.7, 5)
