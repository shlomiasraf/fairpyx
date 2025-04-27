from typing import List, Dict, Any
from fairpyx.instances import Instance

def create_instance_from_approvals_and_costs(approvals: List[List[int]], costs: List[float], budget: float) -> Instance:
    """
    Utility to convert approval-based input into a format accepted by fairpyx.Instance.
    Each agent gets value 1 for approved items, 0 otherwise.
    """
    num_agents = len(approvals)
    num_items = len(costs)

    if num_agents == 0 or num_items == 0:
        dummy_valuations = {0: {0: 0}}
        dummy_agent_capacities = {0: 1}
        dummy_item_capacities = {0: 1}
        dummy_item_weights = {0: 1}
        return Instance(
            valuations=dummy_valuations,
            agent_capacities=dummy_agent_capacities,
            item_capacities=dummy_item_capacities,
            item_weights=dummy_item_weights
        )

    valuations: Dict[Any, Dict[Any, int]] = {}

    for i in range(num_agents):
        valuations[i] = {}
        for j in range(num_items):
            valuations[i][j] = 1 if j in approvals[i] else 0

    agent_capacities = {i: budget for i in range(num_agents)}
    item_capacities = {j: 1000 for j in range(num_items)}
    item_weights = {j: costs[j] for j in range(num_items)}

    return Instance(
        valuations=valuations,
        agent_capacities=agent_capacities,
        item_capacities=item_capacities,
        item_weights=item_weights
    )
