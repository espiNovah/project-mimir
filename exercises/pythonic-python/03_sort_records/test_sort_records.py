from sort_records import cheapest, rank_results

RESULTS = [
    {"name": "doc-b", "score": 0.7},
    {"name": "doc-a", "score": 0.9},
    {"name": "doc-c", "score": 0.7},
    {"name": "doc-d", "score": 0.2},
]


def test_highest_score_first():
    assert [r["name"] for r in rank_results(RESULTS)][0] == "doc-a"


def test_ties_broken_by_name():
    assert [r["name"] for r in rank_results(RESULTS)] == ["doc-a", "doc-b", "doc-c", "doc-d"]


def test_input_not_changed():
    before = list(RESULTS)
    rank_results(RESULTS)
    assert RESULTS == before


def test_cheapest():
    models = [
        {"name": "big", "price": 15.0},
        {"name": "small", "price": 0.8},
        {"name": "medium", "price": 3.0},
    ]
    assert cheapest(models, 2) == ["small", "medium"]


def test_cheapest_n_larger_than_list():
    assert cheapest([{"name": "only", "price": 1}], 5) == ["only"]
