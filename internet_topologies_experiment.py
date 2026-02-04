# The script that tests the routing algorithms on real Internet topologies
# Author: Leon Okida
# Last modification: 02/03/2026

from routing_sim.routing_algorithms.max_flow_routing import MaxFlowRouting
from routing_sim.routing_algorithms.probabilistic_max_flow_routing import ProbabilisticMaxFlowRouting
from routing_sim.routing_algorithms.dijkstra_routing import DijsktraRouting
from routing_sim.routing_algorithms.arborescence_routing import ArborescenceRouting

from routing_sim.simulation_engine.frr_simulation_engine import FRRSimulationEngine
from routing_sim.simulation_engine.arborescence_simulation_engine import ArborescenceSimulationEngine

from routing_sim.network import Network
from routing_sim.topology_generation import read_graph, remove_low_connectivity_vertices

import sys
import random
import copy

# ---------------- Utils ----------------

def sample_non_edges(G, k):
    nodes = list(G.nodes())
    samples = set()

    while len(samples) < k:
        u, v = random.sample(nodes, 2)
        if not G.has_edge(u, v):
            samples.add(tuple(sorted((u, v))))
    
    return list(samples)

# ---------------- Setup ----------------

topology = remove_low_connectivity_vertices(read_graph(sys.argv[1]))
file_name = sys.argv[2]

SAMPLE_SIZE = 30
trips = sample_non_edges(topology, SAMPLE_SIZE)

# Factories to avoid reusing instances on more than one execution
arbo_algo = ArborescenceRouting()
arbo_algo.compute_arborescence_packing(topology)
algorithm_factories = [
    lambda: DijsktraRouting(),
    lambda: MaxFlowRouting(0.2),
    lambda: MaxFlowRouting(0.5),
    lambda: MaxFlowRouting(0.8),
    lambda: ProbabilisticMaxFlowRouting(0.5, 0.1),
    lambda: ProbabilisticMaxFlowRouting(1, 0.1),
    lambda: ProbabilisticMaxFlowRouting(2, 0.1),
    lambda: copy.deepcopy(arbo_algo),
]

engine_factories = {
    "Dijkstra": FRRSimulationEngine,
    "Probabilistic MaxFlowRouting": FRRSimulationEngine,
    "MaxFlowRouting": FRRSimulationEngine,
    "Arborescence": ArborescenceSimulationEngine,
}

# ---------------- Experiment ----------------

for make_algorithm in algorithm_factories:
    algorithm = make_algorithm()
    print(f"Current Algorithm: {algorithm.name}")

    for u, v in trips:

        # Create network from topology
        network = Network.from_networkx_graph(topology)

        # Loads engine
        for engine_name in engine_factories.keys():
            if engine_name in algorithm.name:
                engine_class = engine_factories[engine_name]
                break
        engine = engine_class(network)

        # Routes without failure
        _, route = engine.simulate_routing(
            u, v, algorithm,
            f"{u}-{v} without failures",
            file_name
        )

        if route is None or len(route) < 3:
            print(f"Error in: {u},{v}")
            print(f"{u}, {v}")
            continue

        # Routes with failure
        idx = random.randrange(len(route) - 1)
        edge_to_fail = (route[idx], route[idx + 1])

        engine.add_edge_failure(edge_to_fail)

        _, route = engine.simulate_routing(
           u, v, algorithm,
           f"{u}-{v} with failure on {edge_to_fail[0]}-{edge_to_fail[1]}",
           file_name
        )

        if route is None or len(route) < 3:
            print(f"Error in: {u},{v}")
            print(f"{u}, {v}")
            continue
