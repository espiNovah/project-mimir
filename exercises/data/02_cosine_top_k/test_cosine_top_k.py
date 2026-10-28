import numpy as np
import pytest

from cosine_top_k import cosine, normalize, top_k


def test_cosine_example():
    a = np.array([1.0, 2.0, 2.0])
    b = np.array([2.0, 0.0, 1.0])
    assert cosine(a, b) == pytest.approx(4 / (3 * np.sqrt(5)))
    assert isinstance(cosine(a, b), float)


def test_cosine_ignores_length():
    a = np.array([1.0, 2.0, 2.0])
    assert cosine(a, 10 * a) == pytest.approx(1.0)
    assert cosine(a, -a) == pytest.approx(-1.0)
    assert cosine(np.array([1.0, 0.0]), np.array([0.0, 3.0])) == pytest.approx(0.0)


def test_normalize_rows():
    m = np.array([[3.0, 4.0], [0.0, 2.0]])
    unit = normalize(m)
    assert unit.shape == (2, 2)
    np.testing.assert_allclose(unit, [[0.6, 0.8], [0.0, 1.0]])
    np.testing.assert_allclose(np.linalg.norm(unit, axis=1), [1.0, 1.0])


def test_normalize_vector():
    np.testing.assert_allclose(normalize(np.array([3.0, 4.0])), [0.6, 0.8])


def test_normalize_does_not_change_input():
    m = np.array([[3.0, 4.0]])
    normalize(m)
    np.testing.assert_allclose(m, [[3.0, 4.0]])


def test_top_k_example():
    docs = np.array([[1.0, 0.0], [0.0, 2.0], [3.0, 3.0]])
    result = top_k(np.array([1.0, 1.0]), docs, k=2)
    assert [i for i, _ in result] == [2, 0]
    assert result[0][1] == pytest.approx(1.0)
    assert result[1][1] == pytest.approx(np.sqrt(0.5))
    assert all(isinstance(i, int) and isinstance(s, float) for i, s in result)


def test_top_k_is_cosine_not_dot_product():
    # The long vector has the biggest dot product but points the wrong way.
    docs = np.array([[100.0, 1.0], [1.0, 1.1]])
    assert top_k(np.array([1.0, 1.0]), docs, k=1)[0][0] == 1


def test_top_k_on_random_embeddings():
    rng = np.random.default_rng(0)
    docs = rng.normal(size=(50, 16))
    query = docs[7] + 0.01 * rng.normal(size=16)  # almost a copy of row 7
    result = top_k(query, docs, k=5)
    assert len(result) == 5
    assert result[0][0] == 7
    scores = [s for _, s in result]
    assert scores == sorted(scores, reverse=True)
