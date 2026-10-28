from code_checks import (
    citations_were_retrieved,
    has_citation,
    is_allowed_label,
    run_checks,
    under_word_limit,
)

ANSWER = "Set the timeout with --timeout [2]. The default is 30 seconds [5]."
LABELS = {"billing", "bug", "feature_request", "other"}


def test_has_citation():
    assert has_citation(ANSWER) is True
    assert has_citation("The default is 30 seconds.") is False
    assert has_citation("See section 2 (page 5).") is False


def test_refusal_needs_no_citation():
    assert has_citation("I don't know. The docs don't say.") is True
    assert has_citation("Sorry, I DON'T KNOW.") is True


def test_citations_were_retrieved():
    assert citations_were_retrieved(ANSWER, 4) is False
    assert citations_were_retrieved(ANSWER, 5) is True
    assert citations_were_retrieved("Bad index [0].", 3) is False
    assert citations_were_retrieved("Two digits [12].", 12) is True
    assert citations_were_retrieved("No citations at all.", 3) is True


def test_under_word_limit():
    assert under_word_limit(ANSWER) is True
    assert under_word_limit("word " * 150) is True
    assert under_word_limit("word " * 151) is False
    assert under_word_limit("one two  three\nfour", limit=4) is True
    assert under_word_limit("one two three four five", limit=4) is False


def test_is_allowed_label():
    assert is_allowed_label("billing", LABELS) is True
    assert is_allowed_label(" billing\n", LABELS) is True
    assert is_allowed_label("Label: billing", LABELS) is False
    assert is_allowed_label("Billing", LABELS) is False
    assert is_allowed_label("", LABELS) is False


def test_run_checks():
    assert run_checks(ANSWER, 4) == {
        "has_citation": True,
        "citations_were_retrieved": False,
        "under_word_limit": True,
    }
