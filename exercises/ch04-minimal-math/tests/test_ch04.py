"""Tests for the chapter 4 exercise. Copy to ai-course/tests/test_ch04.py and run: uv run pytest -q"""

import numpy as np
import pytest

from ch04.gradient_descent import descend, loss
from ch04.softmax_temperature import negative_log_likelihood, softmax
from ch04.vectors import cosine, dot, norm, normalize, rank


def test_dot_and_norm() -> None:
    assert dot([1, 2], [3, 4]) == 11.0
    assert norm([3, 4]) == 5.0


def test_cosine_same_direction_is_one_and_orthogonal_is_zero() -> None:
    assert cosine([3, 4], [6, 8]) == pytest.approx(1.0)
    assert cosine([1, 0], [0, 1]) == pytest.approx(0.0)


def test_cosine_rejects_zero_vector_and_shape_mismatch() -> None:
    with pytest.raises(ValueError):
        cosine([0, 0], [1, 1])
    with pytest.raises(ValueError):
        cosine([1, 2, 3], [1, 2])


def test_normalize_has_unit_length() -> None:
    assert np.linalg.norm(normalize([3, 4])) == pytest.approx(1.0)


def test_rank_puts_best_match_first() -> None:
    ranked = rank([1, 0], {"a": [0.9, 0.1], "b": [0.1, 0.9]})
    assert [name for name, _ in ranked] == ["a", "b"]


def test_softmax_sums_to_one_and_keeps_order() -> None:
    probs = softmax([2.0, 1.0, 0.0])
    assert probs.sum() == pytest.approx(1.0)
    assert probs[0] > probs[1] > probs[2]
    assert np.round(probs, 3).tolist() == [0.665, 0.245, 0.09]


def test_lower_temperature_is_sharper() -> None:
    sharp = softmax([2.0, 1.0, 0.0], temperature=0.5)
    flat = softmax([2.0, 1.0, 0.0], temperature=2.0)
    assert sharp[0] > flat[0]


def test_loss_grows_as_probability_of_correct_shrinks() -> None:
    assert negative_log_likelihood(0.8) == pytest.approx(0.223, abs=1e-3)
    assert negative_log_likelihood(0.2) == pytest.approx(1.609, abs=1e-3)
    assert negative_log_likelihood(1.0) == 0.0


def test_gradient_descent_converges_with_a_sane_rate_and_diverges_with_a_bad_one() -> None:
    *_, (_, w_final, loss_final) = descend(0.0, learning_rate=0.1, steps=100)
    assert abs(w_final - 3.0) < 1e-3 and loss_final < 1e-6
    *_, (_, _, loss_bad) = descend(0.0, learning_rate=1.1, steps=5)
    assert loss_bad > loss(0.0)
