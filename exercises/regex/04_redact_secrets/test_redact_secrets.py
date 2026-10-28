from redact_secrets import count_redactions, redact


def test_key_and_email():
    assert redact("key=sk-abc123XYZ789 owner=ada@example.com") == "key=[API_KEY] owner=[EMAIL]"


def test_key_with_dashes_and_underscores():
    assert redact("Authorization: sk-proj_AB-12cd34EF") == "Authorization: [API_KEY]"


def test_short_sk_is_left_alone():
    assert redact("use sk-short as a placeholder") == "use sk-short as a placeholder"


def test_multiple_and_punctuation_kept():
    text = "Ask ada@example.com, or grace@example.org."
    assert redact(text) == "Ask [EMAIL], or [EMAIL]."


def test_clean_text_unchanged():
    text = "Nothing secret here: model=cheap, 42 tokens."
    assert redact(text) == text


def test_count_redactions():
    text = "sk-aaaaaaaaaa and sk-bbbbbbbbbb belong to ops@example.com"
    assert count_redactions(text) == {"api_keys": 2, "emails": 1}
    assert count_redactions("") == {"api_keys": 0, "emails": 0}
