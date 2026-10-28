from average_lengths import average_lengths


def test_clean_names_still_work():
    replies = [
        {"model": "cheap", "text": "Paris."},
        {"model": "cheap", "text": ""},
    ]
    assert average_lengths(replies) == {"cheap": 3.0}


def test_case_and_spaces_are_the_same_model():
    replies = [
        {"model": "cheap", "text": "Paris."},
        {"model": "Capable ", "text": "Paris, of course."},
        {"model": "capable", "text": "The capital is Paris."},
    ]
    assert average_lengths(replies) == {"cheap": 6.0, "capable": 19.0}


def test_keys_are_lowercase():
    assert list(average_lengths([{"model": " CHEAP", "text": "ok"}])) == ["cheap"]


def test_empty_input():
    assert average_lengths([]) == {}
