# The script that tests the routing algorithms on real Internet topologies
# Author: Leon Okida
# Last modification: 02/01/2026
# Usage: python3 internet_topologies_experiment.py <topology_file_name> <results_file_name>

# Simulator imports
# Algorithms
from routing_sim.routing_algorithms.max_flow_routing import MaxFlowRouting
from routing_sim.routing_algorithms.probabilistic_max_flow_routing import ProbabilisticMaxFlowRouting
from routing_sim.routing_algorithms.dijkstra_routing import DijsktraRouting
from routing_sim.routing_algorithms.arborescence_routing import ArborescenceRouting
# Engines
from routing_sim.simulation_engine.frr_simulation_engine import FRRSimulationEngine
from routing_sim.simulation_engine.arborescence_simulation_engine import ArborescenceSimulationEngine
# Utils
from routing_sim.network import Network
from routing_sim.routing_algorithms.interface import RoutingAlgorithm
from routing_sim.simulation_engine.interface import SimulationEngine
from routing_sim.topology_generation import read_graph

# Other
import sys
import networkx as nx
import random

def sample_non_edges(G, k):
    nodes = list(G.nodes())
    samples = set()

    while len(samples) < k:
        u, v = random.sample(nodes, 2)
        if not G.has_edge(u, v):
            samples.add(tuple(sorted((u, v))))  # elimina (v,u)
    
    return list(samples)

# Loads topology
topology = read_graph(sys.argv[1])
network = Network.from_networkx_graph(topology)
network.remove_low_connectivity_routers()

# Prepares each algorithm and engine for the experiments
experiments: list[tuple[RoutingAlgorithm, SimulationEngine]] = [
    (DijsktraRouting(), FRRSimulationEngine(network, False)),
    (MaxFlowRouting(0.2), FRRSimulationEngine(network, False)),
    (MaxFlowRouting(0.5), FRRSimulationEngine(network, False)),
    (MaxFlowRouting(0.8), FRRSimulationEngine(network, False)),
    (ProbabilisticMaxFlowRouting(0.5, 0.1), FRRSimulationEngine(network, False)),
    (ProbabilisticMaxFlowRouting(1, 0.1), FRRSimulationEngine(network, False)),
    (ProbabilisticMaxFlowRouting(2, 0.1), FRRSimulationEngine(network, False)),
    (ArborescenceRouting(), ArborescenceSimulationEngine(network, False)),
]

# Gets the file to store the results
file_name = sys.argv[2]

# Creates trips for the experiment
SAMPLE_SIZE = 30
trips = sample_non_edges(network.topology, SAMPLE_SIZE)

# Begins the experiment
for algorithm, engine in experiments:
    print(f"Current Algorithm: {algorithm.name}")
    if algorithm.name == "Arborescence Routing":
        algorithm.compute_arborescence_packing(network.topology)

    for u, v in trips:
        # First, runs the experiment without a failure
        _, route = engine.simulate_routing(u, v, algorithm, f"{u}-{v} without failures", file_name)
        if route is None or len(route) < 3:
            print("deu algum erro, investigar:")
            print(f"{u}, {v}")
            continue

        # Then, adds a failure in one of the edges and simulates the routing again
        idx = random.randrange(len(route) - 1)
        edge_to_fail = (route[idx], route[idx+1])
        engine.add_edge_failure(edge_to_fail)
        _, _ = engine.simulate_routing(u, v, algorithm, f"{u}-{v} with failure on {edge_to_fail[0]}-{edge_to_fail[1]}", file_name)

        # Clears failures
        engine.clean_edge_failures()