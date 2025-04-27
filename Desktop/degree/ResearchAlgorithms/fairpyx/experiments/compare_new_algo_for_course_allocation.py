"""
Compare the performance of algorithms for fair course allocation.

Programmer: Erel Segal-Halevi
Since: 2023-07
"""

######### COMMON VARIABLES AND ROUTINES ##########

from fairpyx import divide, AgentBundleValueMatrix, Instance
import fairpyx.algorithms as crs
from typing import *
import numpy as np
import cvxpy as cp
import logging
from fairpyx.explanations import ConsoleExplanationLogger, FilesExplanationLogger, StringsExplanationLogger
console_explanation_logger = ConsoleExplanationLogger(level=logging.DEBUG)

max_value = 1000
normalized_sum_of_values = 1000
TIME_LIMIT = 300

algorithms_with_specific_solver = [
    crs.TTC_O_function,
    crs.SP_O_function,
    crs.OC_function,
]

algorithm_only_oc = [
    crs.OC_function,
]

algorithms_with_none_solver = [
    crs.iterated_maximum_matching_unadjusted,
    crs.iterated_maximum_matching_adjusted,
    crs.TTC_function,
    crs.SP_function,
]

def evaluate_algorithm_on_instance(algorithm, instance, solver):
    if algorithm in algorithms_with_none_solver:
        allocation = divide(algorithm, instance)
    else:
        allocation = divide(algorithm, instance, solver=solver, explanation_logger=console_explanation_logger)
    matrix = AgentBundleValueMatrix(instance, allocation)
    matrix.use_normalized_values()
    return {
        "utilitarian_value": matrix.utilitarian_value(),
        "egalitarian_value": matrix.egalitarian_value(),
        "max_envy": matrix.max_envy(),
        "mean_envy": matrix.mean_envy(),
        "max_deficit": matrix.max_deficit(),
        "mean_deficit": matrix.mean_deficit(),
        "num_with_top_1": matrix.count_agents_with_top_rank(1),
        "num_with_top_2": matrix.count_agents_with_top_rank(2),
        "num_with_top_3": matrix.count_agents_with_top_rank(3),
        "solver": solver,
    }

######### EXPERIMENT WITH UNIFORMLY-RANDOM DATA ##########

def course_allocation_with_random_instance_uniform(
    num_of_agents:int, num_of_items:int,
    value_noise_ratio:float,
    algorithm:Callable,
    random_seed: int, solver):
    agent_capacity_bounds = [6,6]
    item_capacity_bounds = [40,40]
    np.random.seed(random_seed)
    instance = Instance.random_uniform(
        num_of_agents=num_of_agents, num_of_items=num_of_items,
        normalized_sum_of_values=normalized_sum_of_values,
        agent_capacity_bounds=agent_capacity_bounds,
        item_capacity_bounds=item_capacity_bounds,
        item_base_value_bounds=[1,max_value],
        item_subjective_ratio_bounds=[1-value_noise_ratio, 1+value_noise_ratio]
        )
    return evaluate_algorithm_on_instance(algorithm, instance, solver)

def run_uniform_experiment():
    experiment = experiments_csv.Experiment("results/", "with_solver_algo_for_course_allocation_uniform.csv", backup_folder="results/backup/")
    input_ranges_none_solver = {
        "num_of_agents": [100,200,300],
        "num_of_items":  [25],
        "value_noise_ratio": [0, 0.2, 0.5, 0.8, 1],
        "algorithm": algorithms_with_none_solver,
        "random_seed": range(5),
        "solver": [None],
    }
    # experiment.run_with_time_limit(course_allocation_with_random_instance_uniform, input_ranges_none_solver, time_limit=TIME_LIMIT)

    input_ranges_specific_solver = {
        "num_of_agents": [100],
        "num_of_items":  [25],
        "value_noise_ratio": [0, 0.2, 0.5, 0.8, 1],
        "algorithm": algorithms_with_specific_solver,
        "random_seed": range(5),
        "solver": [None, cp.CBC, cp.MOSEK, cp.SCIP, cp.XPRESS], #, cp.COPT, cp.CPLEX, cp.GUROBI
    }
    # experiment.run_with_time_limit(course_allocation_with_random_instance_uniform, input_ranges_specific_solver, time_limit=TIME_LIMIT)

    input_ranges_specific_solver = {
        "num_of_agents": [200, 300],
        "num_of_items": [25],
        "value_noise_ratio": [0, 0.2, 0.5, 0.8, 1],
        "algorithm": algorithms_with_specific_solver,
        "random_seed": range(5),
        "solver": [None, cp.CBC, cp.MOSEK, cp.SCIP],  #, cp.XPRESS , cp.COPT, cp.CPLEX, cp.GUROBI
    }
    # experiment.run_with_time_limit(course_allocation_with_random_instance_uniform, input_ranges_specific_solver, time_limit=TIME_LIMIT)

    input_ranges_specific_solver = {
        "num_of_agents": [100, 200, 300],
        "num_of_items": [25],
        "value_noise_ratio": [0, 0.2, 0.5, 0.8, 1],
        "algorithm": algorithms_with_specific_solver,
        "random_seed": range(5),
        "solver": [cp.SCIPY]
    }
    experiment.run_with_time_limit(course_allocation_with_random_instance_uniform, input_ranges_specific_solver, time_limit=TIME_LIMIT)


######### EXPERIMENT WITH DATA GENERATED ACCORDING TO THE SZWS MODEL ##########

def course_allocation_with_random_instance_szws(
    num_of_agents:int, num_of_items:int,
    agent_capacity:int,
    supply_ratio:float,
    num_of_popular_items:int,
    mean_num_of_favorite_items:float,
    favorite_item_value_bounds:tuple[int,int],
    nonfavorite_item_value_bounds:tuple[int,int],
    algorithm:Callable,
    random_seed: int, solver):
    np.random.seed(random_seed)
    instance = Instance.random_szws(
        num_of_agents=num_of_agents, num_of_items=num_of_items, normalized_sum_of_values=normalized_sum_of_values,
        agent_capacity=agent_capacity,
        supply_ratio=supply_ratio,
        num_of_popular_items=num_of_popular_items,
        mean_num_of_favorite_items=mean_num_of_favorite_items,
        favorite_item_value_bounds=favorite_item_value_bounds,
        nonfavorite_item_value_bounds=nonfavorite_item_value_bounds,
        )
    return evaluate_algorithm_on_instance(algorithm, instance, solver)

def run_szws_experiment():
    experiment = experiments_csv.Experiment("results/", "with_solver_algo_for_course_allocation_szws.csv", backup_folder="results/backup/")
    input_ranges_none_solver = {
        "num_of_agents": [100,200,300],
        "num_of_items":  [25],
        "agent_capacity": [5],
        "supply_ratio": [1.1, 1.25, 1.5],
        "num_of_popular_items": [6, 9],
        "mean_num_of_favorite_items": [2.6, 3.85],
        "favorite_item_value_bounds": [(50,100)],
        "nonfavorite_item_value_bounds": [(0,50)],
        "algorithm": algorithms_with_none_solver,
        "random_seed": range(5),
        "solver": [None],
    }
    # experiment.run_with_time_limit(course_allocation_with_random_instance_szws, input_ranges_none_solver, time_limit=TIME_LIMIT)

    input_ranges_specific_solver = {
        "num_of_agents": [100],
        "num_of_items":  [25],
        "agent_capacity": [5],
        "supply_ratio": [1.1, 1.25, 1.5],
        "num_of_popular_items": [6, 9],
        "mean_num_of_favorite_items": [2.6, 3.85],
        "favorite_item_value_bounds": [(50,100)],
        "nonfavorite_item_value_bounds": [(0,50)],
        "algorithm": algorithms_with_specific_solver,
        "random_seed": range(5),
        "solver": [None, cp.CBC, cp.MOSEK, cp.SCIP, cp.XPRESS], #, cp.COPT, cp.CPLEX, cp.GUROBI
    }
    # experiment.run_with_time_limit(course_allocation_with_random_instance_szws, input_ranges_specific_solver, time_limit=TIME_LIMIT)

    input_ranges_specific_solver = {
        "num_of_agents": [200, 300],
        "num_of_items": [25],
        "agent_capacity": [5],
        "supply_ratio": [1.1, 1.25, 1.5],
        "num_of_popular_items": [6, 9],
        "mean_num_of_favorite_items": [2.6, 3.85],
        "favorite_item_value_bounds": [(50, 100)],
        "nonfavorite_item_value_bounds": [(0, 50)],
        "algorithm": algorithms_with_specific_solver,
        "random_seed": range(5),
        "solver": [None, cp.CBC, cp.MOSEK, cp.SCIP],  #, cp.XPRESS , cp.COPT, cp.CPLEX, cp.GUROBI
    }
    # experiment.run_with_time_limit(course_allocation_with_random_instance_szws, input_ranges_specific_solver, time_limit=TIME_LIMIT)

    input_ranges_specific_solver = {
        "num_of_agents": [100, 200, 300],
        "num_of_items": [25],
        "agent_capacity": [5],
        "supply_ratio": [1.1, 1.25, 1.5],
        "num_of_popular_items": [6, 9],
        "mean_num_of_favorite_items": [2.6, 3.85],
        "favorite_item_value_bounds": [(50, 100)],
        "nonfavorite_item_value_bounds": [(0, 50)],
        "algorithm": algorithms_with_specific_solver,
        "random_seed": range(5),
        "solver": [cp.SCIPY]
    }
    experiment.run_with_time_limit(course_allocation_with_random_instance_szws, input_ranges_specific_solver, time_limit=TIME_LIMIT)



######### EXPERIMENT WITH DATA SAMPLED FROM ARIEL 5783 DATA ##########

import json
filename = "data/ariel_5783_input.json"
with open(filename, "r", encoding="utf-8") as file:
    ariel_5783_input = json.load(file)

def course_allocation_with_random_instance_sample(
    max_total_agent_capacity:int,
    algorithm:Callable,
    random_seed: int, solver):
    np.random.seed(random_seed)
    (valuations, agent_capacities, item_capacities, agent_conflicts, item_conflicts) = \
        (ariel_5783_input["valuations"], ariel_5783_input["agent_capacities"], ariel_5783_input["item_capacities"], ariel_5783_input["agent_conflicts"], ariel_5783_input["item_conflicts"])
    instance = Instance.random_sample(
        max_num_of_agents = max_total_agent_capacity,
        max_total_agent_capacity = max_total_agent_capacity,
        prototype_agent_conflicts=agent_conflicts,
        prototype_agent_capacities=agent_capacities,
        prototype_valuations=valuations,
        item_capacities=item_capacities,
        item_conflicts=item_conflicts)
    return evaluate_algorithm_on_instance(algorithm, instance, solver)

def run_ariel_experiment():
    experiment = experiments_csv.Experiment("results/", "with_solver_algo_for_course_allocation_ariel.csv", backup_folder="results/backup/")
    input_ranges_none_solver = {
        "max_total_agent_capacity": [1000, 1115, 1500, 2000],
        "algorithm": algorithms_with_none_solver,
        "random_seed": range(10),
        "solver": [cp.CBC, cp.MOSEK, cp.SCIP, cp.SCIPY]
    }
    # experiment.run_with_time_limit(course_allocation_with_random_instance_sample, input_ranges_none_solver, time_limit=TIME_LIMIT)

    input_ranges_specific_solver = {
        "max_total_agent_capacity": [1000, 1115, 1500, 2000],
        "algorithm": algorithms_with_specific_solver,
        "random_seed": range(10),
        "solver": [cp.XPRESS]
    }
    experiment.run_with_time_limit(course_allocation_with_random_instance_sample, input_ranges_specific_solver, time_limit=TIME_LIMIT)

#######TEST FOR OC##########
def run_uniform_oc_experiment():
    experiment = experiments_csv.Experiment("results/", "test_for_oc_course_allocation_uniform.csv", backup_folder="results/backup/")
    input_ranges_none_solver = {
        "num_of_agents": [300],
        "num_of_items":  [25],
        "value_noise_ratio": [0.5],
        "algorithm": algorithm_only_oc,
        "random_seed": range(1,2),
        "solver": [cp.SCIPY],
    }
    experiment.run_with_time_limit(course_allocation_with_random_instance_uniform, input_ranges_none_solver, time_limit=TIME_LIMIT)

######### MAIN PROGRAM ##########

if __name__ == "__main__":
    import logging, experiments_csv
    experiments_csv.logger.setLevel(logging.DEBUG)

    from fairpyx.algorithms.Optimization_based_Mechanisms.TTC import logger as TTC_logger

    # TTC_logger.setLevel(logging.INFO)
    # TTC_logger.addHandler(logging.StreamHandler())
    #run_uniform_experiment() #done
    #run_szws_experiment() #done
    # run_ariel_experiment() #done
    run_uniform_oc_experiment()