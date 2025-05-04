"""
Tests for the gpseq algorithm using approval-based budgeting instances.

Author: Shlomi Asraf
Since: 2024-04
"""

import pytest
import logging
import random
from fairpyx.algorithms.gpseq import gpseq
from fairpyx.utils.gpseq_instance_utils import create_instance_from_approvals_and_costs

logger = logging.getLogger(__name__)

@pytest.mark.parametrize("approvals, costs, budget, expected", [
    ([[0], [0], [1], [1]], [2, 2, 1], 3, [0, 2]),
    ([[0]], [1], 1, [0]),
    ([[0], [0], [0], [1]], [1, 2], 2, [0]),
    ([[0, 1], [0, 1], [0, 1], [0, 1], [2], [2]], [2, 1.5, 1.5], 3, [1, 2]),
    ([[0, 1], [0, 1], [0, 1], [0, 1], [2], [2]], [2, 2, 0.8], 2, [2]),
    ([[0, 1], [0], [1, 2], [2]], [1.5, 1.5, 1], 3, [0, 2]),
])
def test_gpseq_examples(approvals, costs, budget, expected):
    logger.info(f"Testing gpseq with approvals={approvals}, costs={costs}, budget={budget}")
    instance = create_instance_from_approvals_and_costs(approvals, costs, budget)
    result = gpseq(instance)
    assert result == expected


def test_gpseq_invalid_budget():
    approvals = [[0]]
    costs = [1.0]
    budget = -5.0
    with pytest.raises(Exception):
        instance = create_instance_from_approvals_and_costs(approvals, costs, budget)
        gpseq(instance)


def test_gpseq_invalid_cost_length():
    approvals = [[0], [1]]
    costs = [1.0]
    budget = 5.0
    with pytest.raises(Exception):
        instance = create_instance_from_approvals_and_costs(approvals, costs, budget)
        gpseq(instance)


def test_gpseq_empty_instance():
    approvals = []
    costs = []
    budget = 3.0
    instance = create_instance_from_approvals_and_costs(approvals, costs, budget)
    result = gpseq(instance)
    assert result == []


def test_gpseq_large_random_input():
    n = 100
    m = 50
    approvals = [random.sample(range(m), random.randint(1, 10)) for _ in range(n)]
    costs = [random.uniform(1.0, 5.0) for _ in range(m)]
    budget = 100.0
    instance = create_instance_from_approvals_and_costs(approvals, costs, budget)
    result = gpseq(instance)
    assert isinstance(result, list)
    assert all(0 <= i < m for i in result)


if __name__ == "__main__":
    import sys
    import pytest
    logging.basicConfig(level=logging.INFO)
    pytest.main(["-v", sys.argv[0]])
