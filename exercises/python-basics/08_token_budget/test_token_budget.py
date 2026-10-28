from token_budget import estimate_tokens, fits_budget


def test_exact_multiple():
    assert estimate_tokens("abcdefgh") == 2


def test_rounds_up():
    assert estimate_tokens("abcde") == 2


def test_empty_text():
    assert estimate_tokens("") == 0


def test_custom_chars_per_token():
    assert estimate_tokens("abcdefgh", chars_per_token=3) == 3


def test_fits_budget_true():
    assert fits_budget(["abcd", "abcd"], budget=2) is True


def test_fits_budget_false():
    assert fits_budget(["abcd", "abcde"], budget=2) is False


def test_fits_budget_passes_chars_per_token_through():
    assert fits_budget(["abcdef"], budget=3, chars_per_token=2) is True
    assert fits_budget(["abcdef"], budget=2, chars_per_token=2) is False


def test_empty_list_fits():
    assert fits_budget([], budget=0) is True
