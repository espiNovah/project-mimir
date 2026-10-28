import time

from crawl_queue import crawl_order


def test_example():
    links = {
        "index": ["install", "guide"],
        "install": ["guide", "faq"],
        "guide": ["api"],
    }
    assert crawl_order("index", links) == ["index", "install", "guide", "faq", "api"]


def test_cycles_visit_each_page_once():
    links = {"a": ["b"], "b": ["a", "c"], "c": ["a"]}
    assert crawl_order("a", links) == ["a", "b", "c"]


def test_breadth_first_not_depth_first():
    links = {"root": ["x", "y"], "x": ["x1"], "y": ["y1"]}
    assert crawl_order("root", links) == ["root", "x", "y", "x1", "y1"]


def test_single_page():
    assert crawl_order("lonely", {}) == ["lonely"]


def test_fast_on_a_wide_site():
    n = 200_000
    links = {"index": [f"page{i}" for i in range(n)]}
    start = time.perf_counter()
    order = crawl_order("index", links)
    elapsed = time.perf_counter() - start
    assert len(order) == n + 1
    assert order[-1] == f"page{n - 1}"
    assert elapsed < 0.5, f"took {elapsed:.2f} s; what does pop(0) cost on a long list?"
