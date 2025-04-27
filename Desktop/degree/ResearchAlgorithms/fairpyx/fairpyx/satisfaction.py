"""
Given an instance and an allocation, calculate various measures of user satisfaction.

Author: Erel Segal-Halevi
Since: 2023-07
"""

from fairpyx import Instance
import numpy as np

from functools import cache


class AgentBundleValueMatrix:

    def __init__(self, instance:Instance, allocation:dict[any, list[any]], normalized=True):
        """
        :param instance: an input instance to the fair-course-allocation problem.
        :param allocation: a dict mapping each agent to its bundle (a list)
        :param normalized: if True, it normalizes the valuations by the max-value.

        >>> instance = Instance(
        ...   agent_capacities = {"Alice": 2, "Bob": 3}, 
        ...   item_capacities  = {"c1": 4, "c2": 5}, 
        ...   valuations       = {"Alice": {"c1": 11, "c2": 22}, "Bob": {"c1": 33, "c2": 44}})
        >>> allocation = {"Alice": ["c1"], "Bob": ["c2"]}
        >>> matrix = AgentBundleValueMatrix(instance, allocation, normalized=False)

        >>> matrix.matrix
        {'Alice': {'Alice': 11, 'Bob': 22}, 'Bob': {'Alice': 33, 'Bob': 44}}
        >>> matrix.utilitarian_value()
        27.5
        >>> matrix.egalitarian_value()
        11

        >>> matrix.make_envy_matrix()
        >>> matrix.envy_matrix
        {'Alice': {'Alice': 0, 'Bob': 11}, 'Bob': {'Alice': -11, 'Bob': 0}}
        >>> matrix.max_envy()
        11
        >>> matrix.mean_envy()
        5.5
        >>> matrix.count_agents_with_top_rank(1)
        1
        >>> matrix.count_agents_with_top_rank(2)
        2
        """
        self.instance = instance
        self.agents = instance.agents
        self.raw_matrix = {
            agent1: {
                agent2: instance.agent_bundle_value(agent1, allocation[agent2])
                for agent2 in self.agents
            }
            for agent1 in self.agents
        }
        self.maximum_values = {
            agent: instance.agent_maximum_value(agent)
            for agent in instance.agents
        }
        self.rankings = {
            agent: instance.agent_ranking(agent, allocation[agent])
            for agent in instance.agents
        }
        self.allocation = {
            agent: sorted(allocation[agent], key=self.rankings[agent].__getitem__)
            for agent in instance.agents
        }
        self.normalized_matrix = {
            agent1: {
                agent2: self.raw_matrix[agent1][agent2] / self.maximum_values[agent1] * 100
                for agent2 in self.agents
            }
            for agent1 in self.agents
        }
        self.matrix = self.raw_matrix
        self.envy_matrix = None  # maps each agent-pair to the envy between them.
        self.envy_vector = None  # maps each agent to his maximum envy.
        if normalized:
            self.use_normalized_values()

    def use_raw_values(self)->float:
        """
        In the computations of utilitarian and egalitarian values, use the raw valuations of the agents.
        """
        if self.matrix!=self.raw_matrix:
           self.matrix = self.raw_matrix
           self.envy_matrix = self.envy_vector = None

    def use_normalized_values(self)->float:
        """
        In the computations of utilitarian and egalitarian values, use the valuations of the agents normalized such that their maximum possible value is 100.
        """
        if self.matrix!=self.normalized_matrix:
           self.matrix = self.normalized_matrix
           self.envy_matrix = self.envy_vector = None

    def utilitarian_value(self)->float:
        return sum([self.matrix[agent][agent] for agent in self.agents])/len(self.agents)

    def egalitarian_value(self)->float:
        return min([self.matrix[agent][agent] for agent in self.agents])

    def make_envy_matrix(self):
        if self.envy_matrix is not None:
            return
        self.envy_matrix = {
            agent1: {
                agent2: self.matrix[agent1][agent2] - self.matrix[agent1][agent1]
                for agent2 in self.agents
            }
            for agent1 in self.agents
        }
        self.envy_vector = {
            agent1: max(self.envy_matrix[agent1].values())
            for agent1 in self.agents
        }

    def max_envy(self):
        self.make_envy_matrix()
        return max(self.envy_vector.values())

    def mean_envy(self):
        self.make_envy_matrix()
        return sum([max(envy,0) for envy in self.envy_vector.values()]) / len(self.agents)

    def egalitarian_value(self):
        return min([self.matrix[agent][agent] for agent in self.agents])

    @cache
    def agent_deficit(self, agent):
        """ A "deficit" is the number of courses the agent received below its capacity. """
        return self.instance.agent_capacity(agent) - len(self.allocation[agent])

    def mean_deficit(self):
        return sum([self.agent_deficit(agent) for agent in self.agents])/len(self.agents)

    def max_deficit(self):
        return max([self.agent_deficit(agent) for agent in self.agents])

    @cache
    def top_rank(self, agent):
        if len(self.allocation[agent])>0:
            return self.rankings[agent][self.allocation[agent][0]]
        else:
            return np.inf
    
    def count_agents_with_top_rank(self, rank=1):
        return sum([self.top_rank(agent)<=rank for agent in self.agents])

    def explain(self, explanation_logger, map_course_to_name:dict={}):
        """
        Generate a verbal explanation for the given agent.
        """
        for agent in self.instance.agents:
            explanation_logger.info("\nHere is your final allocation: ", agents=agent)
            for item in self.allocation[agent]:
                explanation_logger.info(f" * Course {map_course_to_name.get(item,item)}: number {self.rankings[agent][item]} in your ranking, with value {self.instance.agent_item_value(agent,item)}", agents=agent)
            explanation_logger.info(f"The maximum possible value you could get for {self.instance.agent_capacity(agent)} courses is {self.maximum_values[agent]}.", agents=agent)
            explanation_logger.info(f"Your total value is {self.raw_matrix[agent][agent]}, which is {np.round(self.normalized_matrix[agent][agent])}% of the maximum.", agents=agent)




if __name__ == "__main__":
    import doctest, sys
    print("\n", doctest.testmod(), "\n")
    sys.exit()

    import algorithms.picking_sequence
    from adaptors import divide

    random_instance = Instance.random_uniform(
        num_of_agents=10, num_of_items=8, 
        agent_capacity_bounds=[2,4], item_capacity_bounds=[5,5], 
        item_base_value_bounds=[1,200], item_subjective_ratio_bounds=[0.5,1.5],
        normalized_sum_of_values=1000)
    allocation = divide(picking_sequence.round_robin,random_instance)
    matrix = AgentBundleValueMatrix(random_instance, allocation)
    # matrix.explain(ConsoleExplanationLogger()) 

