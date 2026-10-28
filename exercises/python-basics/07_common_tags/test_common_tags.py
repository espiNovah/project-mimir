from common_tags import all_tags, common_tags


def test_common_basic():
    assert common_tags(["python", "ai", "web"], ["ai", "python", "data"]) == ["ai", "python"]


def test_common_ignores_case():
    assert common_tags(["Python"], ["PYTHON", "rust"]) == ["python"]


def test_common_no_repeats():
    assert common_tags(["ai", "ai", "AI"], ["ai"]) == ["ai"]


def test_common_nothing_shared():
    assert common_tags(["a"], ["b"]) == []


def test_all_tags():
    assert all_tags(["web", "AI"], ["ai", "data"]) == ["ai", "data", "web"]


def test_all_tags_empty():
    assert all_tags([], []) == []
