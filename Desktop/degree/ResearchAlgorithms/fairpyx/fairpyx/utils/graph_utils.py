"""
Utility functions using graph algorithms.

Currently contains a single function: many_to_many_matching, which finds a maximum-weight many-to-many matching in a bipartite graph.

Author: Erel Segal-Halevi
Since : 2023-10
"""

import networkz as nx
from collections import defaultdict
from itertools import product

def many_to_many_matching(item_capacities: dict[any,int], agent_capacities:dict[any,int], valuations:dict[any,dict[any,int]], agent_entitlement:callable=lambda x:1)->nx.Graph:
    """
    Computes a many-to-many matching of items to agents.

    >>> from fairpyx.utils.test_utils import stringify

    >>> valuations = {"a":{"x":11, "y":22}, "b":{"x":33,"y":55}}
    >>> stringify(many_to_many_matching(item_capacities={"x":2, "y":2}, agent_capacities={"a":1, "b":1}, valuations=valuations))
    "{a:['y'], b:['y']}"
    >>> stringify(many_to_many_matching(item_capacities={"x":3, "y":1}, agent_capacities={"a":1, "b":1}, valuations=valuations))
    "{a:['x'], b:['y']}"
    >>> stringify(many_to_many_matching(item_capacities={"x":2, "y":2}, agent_capacities={"a":1, "b":2}, valuations=valuations))
    "{a:['y'], b:['x', 'y']}"
    >>> stringify(many_to_many_matching(item_capacities={"x":2, "y":2}, agent_capacities={"a":1, "b":3}, valuations=valuations))
    "{a:['y'], b:['x', 'y']}"

    # Negative valuations
    >>> valuations = {"a":{"x":11, "y":22}, "b":{"x":33,"y":-1}}
    >>> stringify(many_to_many_matching(item_capacities={"x":2, "y":2}, agent_capacities={"a":1, "b":3}, valuations=valuations))
    "{a:['y'], b:['x']}"
    >>> stringify(many_to_many_matching(item_capacities={0:1, 1:1, 2:1, 3:1}, agent_capacities={0:2, 1:2}, valuations=[[5,4,3,2],[2,3,4,5]]))
    '{0:[0, 1], 1:[2, 3]}'
    """
    # subroutine = many_to_many_matching_using_node_cloning
    subroutine = many_to_many_matching_using_network_flow
    return subroutine(
        items = item_capacities.keys(), 
        item_capacity = item_capacities.__getitem__,
        agents = agent_capacities.keys(),
        agent_capacity = agent_capacities.__getitem__,
        agent_item_value = lambda agent,item: valuations[agent][item],
        agent_entitlement = agent_entitlement)


def agent_str(agent):
    return agent if isinstance(agent,str) else f"A{agent}"
def item_str(item):
    return item if isinstance(item,str) else f"I{item}"

def many_to_many_matching_using_network_flow(items:list, item_capacity: callable, agents:list, agent_capacity: callable, agent_item_value:callable, agent_entitlement:callable=lambda x:1, allow_negative_value_assignments=False)->nx.Graph:
    """
    Computes a many-to-many matching of items to agents. 
    
    Algorithm: reduction to min-cost-max-flow.  Based on answer by D.W. https://cs.stackexchange.com/a/161151/1342
    """
    ### a. Construct the flow network:
    graph = nx.DiGraph()
    graph.add_nodes_from(["s", "t"])
    for agent in agents:
        graph.add_edge("s", agent_str(agent), capacity=agent_capacity(agent), weight=0)
    for agent,item in product(agents,items):
        value =  agent_item_value(agent, item)
        if value<0 and not allow_negative_value_assignments:
            continue
        weight = value * agent_entitlement(agent)
        graph.add_edge(agent_str(agent), item_str(item), capacity=1, weight=-weight)
    for item in items:
        graph.add_edge(item_str(item), "t", capacity=item_capacity(item), weight=0)

    ### b. Compute the max-flow min-cost flow:
    flow = nx.max_flow_min_cost(graph, "s", "t", capacity="capacity", weight="weight")

    ### c. Convert the flow to a many-to-many matching:
    map_agent_name_to_bundle = {}
    for agent in agents:
        map_agent_name_to_bundle[agent] = []
        for item in items:
            agent_item_flow =  flow[agent_str(agent)].get(item_str(item),0)
            if agent_item_flow==1:
                map_agent_name_to_bundle[agent].append(item)
            elif agent_item_flow!=0:
                raise ValueError(f"non-binary flow in network: agent={agent}, item={item}, flow={itemflow}.\n Entire flow: {flow}")
        map_agent_name_to_bundle[agent].sort()
    return map_agent_name_to_bundle


def many_to_many_matching_using_node_cloning(items:list, item_capacity: callable, agents:list, agent_capacity: callable, agent_item_value:callable, agent_entitlement:callable=lambda x:1)->nx.Graph:
    """
    Computes a many-to-many matching of items to agents. 
    
    Algorithm: reduction to bipartite matching by vertex cloning. Very inefficient when the capacities are high.
    """
    ### a. Construct the bipartite graph:
    graph = nx.Graph()
    for agent in agents:
        num_of_agent_clones = agent_capacity(agent)
        for item in items:
            weight =  agent_item_value(agent, item)
            weight *= agent_entitlement(agent)
            num_of_item_units = item_capacity(item)

            if num_of_item_units==1 and num_of_agent_clones==1:
                graph.add_edge(agent, item, weight=weight)
            elif num_of_item_units!=1 and num_of_agent_clones==1:
                for unit in range(num_of_item_units):
                    graph.add_edge(agent, (item,unit), weight=weight)
            elif num_of_item_units==1 and num_of_agent_clones!=1:
                for clone in range(num_of_agent_clones):
                    graph.add_edge((agent, clone), item, weight=weight)
            else:
                for clone in range(num_of_agent_clones):
                    for unit in range(num_of_item_units):
                        graph.add_edge((agent, clone), (item,unit), weight=weight)

    ### b. Compute the max-weight matching:
    matching = nx.max_weight_matching(graph, maxcardinality=False)

    ### c. Convert the matching to an assignment:
    # utility function to remove the unit-index from a tuple representing a single unit of an item or agent
    def _remove_unit_index(id):
        if isinstance(id, tuple):  # when there are several units of the same item or agent...
            return id[0]           # ... 0 is the item/agent, 1 is the unit-number. 
        else:
            return id
    map_agent_name_to_bundle = defaultdict(list)
    for edge in matching:
        edge = (_remove_unit_index(edge[0]), _remove_unit_index(edge[1]))
        if edge[0] in agents:  
            (agent,item)=edge
        elif edge[1] in agents:
            (item,agent)=edge
        else:
            raise ValueError(f"Cannot find an agent in {edge}")
        map_agent_name_to_bundle[agent].append(item)
    return map_agent_name_to_bundle



if __name__ == "__main__":
    import doctest
    print(doctest.testmod(report=True,optionflags=doctest.NORMALIZE_WHITESPACE))

    import numpy as np
    matrix = np.array([
        [1, 2, 3], 
        [4, 1, 2], 
        [3, 6, 1]])
    agent_vector = np.array([1, 1, 1])
    task_vector = np.array([1, 1, 1])

    item_capacities = {f"item_{i}": task_vector[i] for i in range(len(task_vector))}
    agent_capacities = {f"agent_{i}": agent_vector[i] for i in range(len(agent_vector))}
    valuations = {f"agent_{i}": {f"item_{j}": matrix[i][j] for j in range(len(matrix[i]))} for i in range(len(matrix))}

    res = many_to_many_matching_using_network_flow(
        items = item_capacities.keys(), 
        item_capacity = item_capacities.__getitem__,
        agents = agent_capacities.keys(),
        agent_capacity = agent_capacities.__getitem__,
        agent_item_value = lambda agent,item: - valuations[agent][item],  # Negative value = cost
        allow_negative_value_assignments=True)  # solve a min-cost problem
    print(f'Faipyx result:\n{res}')
