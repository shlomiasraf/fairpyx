"""
An implementation of the algorithm from:

"Proportionally Representative Participatory Budgeting: Axioms and Algorithms"
by Haris Aziz, Bettina Bäuerle, and Clemens Schwitzgebel (2019), https://arxiv.org/abs/1711.08226

Programmer: Shlomi Asraf
Date: 2024-04-23
"""


from typing import List, Set
from fairpyx import AllocationBuilder
from fairpyx.utils.gpseq_instance_utils import create_instance_from_approvals_and_costs

def gpseq(alloc: AllocationBuilder) -> List[int]:
    """
    Allocates projects using the GPseq algorithm, selecting projects step-by-step to minimize the max load.

    :param alloc: AllocationBuilder instance representing the current state of approvals and budget.
    :return: List of selected project indices.

    Examples:
    >>> approvals = [[0], [0], [1], [1]]
    >>> costs = [2, 2, 1]
    >>> budget = 3
    >>> instance = create_instance_from_approvals_and_costs(approvals, costs, budget)
    >>> gpseq(instance)
    [0,2]

    >>> approvals = [[0]]
    >>> costs = [1]
    >>> budget = 1
    >>> instance = create_instance_from_approvals_and_costs(approvals, costs, budget)
    >>> gpseq(instance)
    [0]

    >>> approvals = [[0], [0], [0], [1]]
    >>> costs = [1, 2]
    >>> budget = 2
    >>> instance = create_instance_from_approvals_and_costs(approvals, costs, budget)
    >>> gpseq(instance)
    [0]

    >>> approvals = [[0,1], [0,1], [0,1], [0,1], [2], [2]]
    >>> costs = [2, 1.5, 1.5]
    >>> budget = 3
    >>> instance = create_instance_from_approvals_and_costs(approvals, costs, budget)
    >>> gpseq(instance)
    [1, 2]

    >>> approvals = [[0,1], [0,1], [0,1], [0,1], [2], [2]]
    >>> costs = [2, 2, 0.8]
    >>> budget = 2
    >>> instance = create_instance_from_approvals_and_costs(approvals, costs, budget)
    >>> gpseq(instance)
    [2]

    >>> approvals = [[0,1], [0], [1,2], [2]]
    >>> costs = [1.5, 1.5, 1]
    >>> budget = 3
    >>> instance = create_instance_from_approvals_and_costs(approvals, costs, budget)
    >>> gpseq(instance)
    [0, 2]
    """
    pass
