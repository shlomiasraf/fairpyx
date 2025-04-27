import pytest
import random
from fairpyx.algorithms.gpseq import gpseq
from fairpyx.utils.gpseq_instance_utils import create_instance_from_approvals_and_costs


def test_gpseq_basic():
    approvals = [[0, 1], [0], [1, 2], [2]]
    costs = [1.5, 1.5, 1.0]
    budget = 3.0
    instance = create_instance_from_approvals_and_costs(approvals, costs, budget)

    selected_projects = gpseq(instance)
    assert isinstance(selected_projects, list)
    assert all(0 <= i < len(costs) for i in selected_projects)


def test_gpseq_empty():
    approvals = []
    costs = []
    budget = 3.0
    instance = create_instance_from_approvals_and_costs(approvals, costs, budget)

    selected_projects = gpseq(instance)
    assert selected_projects == []


def test_gpseq_large_budget():
    approvals = [[0], [0], [0]]
    costs = [1.0]
    budget = 100.0
    instance = create_instance_from_approvals_and_costs(approvals, costs, budget)

    selected_projects = gpseq(instance)
    assert selected_projects == [0]


def test_gpseq_large_random_input():
    n = 100
    m = 50
    approvals = [random.sample(range(m), random.randint(1, 10)) for _ in range(n)]
    costs = [random.uniform(1.0, 5.0) for _ in range(m)]
    budget = 100.0
    instance = create_instance_from_approvals_and_costs(approvals, costs, budget)

    selected_projects = gpseq(instance)
    assert isinstance(selected_projects, list)
    assert all(0 <= i < m for i in selected_projects)
