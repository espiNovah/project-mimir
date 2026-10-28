from extract_emails import extract_emails


def test_two_addresses_in_order():
    text = "Contact ada@example.com or grace@example.org for access."
    assert extract_emails(text) == ["ada@example.com", "grace@example.org"]


def test_trailing_full_stop_is_not_included():
    assert extract_emails("Email me at ada@example.com.") == ["ada@example.com"]


def test_dots_plus_and_subdomains():
    text = "Send results to grace.hopper+evals@mail.example.org, thanks"
    assert extract_emails(text) == ["grace.hopper+evals@mail.example.org"]


def test_handles_are_not_emails():
    assert extract_emails("Follow @mimir and @ada on social media") == []


def test_no_emails():
    assert extract_emails("") == []
    assert extract_emails("nothing to see here") == []


def test_duplicates_are_kept():
    text = "ops@example.com, then ops@example.com again"
    assert extract_emails(text) == ["ops@example.com", "ops@example.com"]
