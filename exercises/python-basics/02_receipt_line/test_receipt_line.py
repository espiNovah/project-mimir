from receipt_line import receipt_line


def test_basic_line():
    assert receipt_line("apple", 3, 0.5) == "3 x apple @ $0.50 = $1.50"


def test_single_item():
    assert receipt_line("notebook", 1, 4.99) == "1 x notebook @ $4.99 = $4.99"


def test_whole_number_price_shows_cents():
    assert receipt_line("coffee", 2, 3) == "2 x coffee @ $3.00 = $6.00"


def test_total_is_rounded_to_cents():
    assert receipt_line("gum", 3, 0.333) == "3 x gum @ $0.33 = $1.00"


def test_returns_a_string():
    assert isinstance(receipt_line("tea", 1, 1.0), str)
