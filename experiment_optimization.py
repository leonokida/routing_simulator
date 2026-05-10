# Experiment testing MaxFlowRouting with different Lambdas to find the best value accross different topologies
# Author: Leon Okida
# Last modification: 05/10/2026

from routing_sim.routing_algorithms.max_flow_routing import MaxFlowRouting
from routing_sim.simulation_engine.simulation_engine import SimulationEngine
from routing_sim.network import Network
from routing_sim.topology_generation import (
    read_graph, 
    remove_low_connectivity_vertices,
    random_graph,
    small_world_graph,
    preferential_attachment_graph
)

import random
import networkx as nx

def sample_non_edges(G: nx.Graph, k: int):
    nodes = list(G.nodes())
    samples = set()

    while len(samples) < k:
        u, v = random.sample(nodes, 2)
        if not G.has_edge(u, v):
            samples.add(tuple(sorted((u, v))))
    
    return list(samples)

def run_experiment(topology_name: str, filename: str, sample_size: int = 30, p: float = 0.1):
    # Factories to avoid reusing instances on more than one execution
    topology_factories = {
        "ChinaNet": lambda: remove_low_connectivity_vertices(read_graph("topologies/chinanet.txt")),
        "Geant": lambda: remove_low_connectivity_vertices(read_graph("topologies/geant.txt")),
        "Internet2": lambda: remove_low_connectivity_vertices(read_graph("topologies/internet2.txt")),
        "RNP": lambda: remove_low_connectivity_vertices(read_graph("topologies/rnp.txt")),
        "Random_80_0.1": lambda: remove_low_connectivity_vertices(random_graph(80, 0.1)),
        "Random_80_0.2": lambda: remove_low_connectivity_vertices(random_graph(80, 0.2)),
        "Random_80_0.3": lambda: remove_low_connectivity_vertices(random_graph(80, 0.3)),
        "Random_100_0.1": lambda: remove_low_connectivity_vertices(random_graph(100, 0.1)),
        "Random_100_0.2": lambda: remove_low_connectivity_vertices(random_graph(100, 0.2)),
        "Random_100_0.3": lambda: remove_low_connectivity_vertices(random_graph(100, 0.3)),
        "Random_120_0.1": lambda: remove_low_connectivity_vertices(random_graph(120, 0.1)),
        "Random_120_0.2": lambda: remove_low_connectivity_vertices(random_graph(120, 0.2)),
        "Random_120_0.3": lambda: remove_low_connectivity_vertices(random_graph(120, 0.3)),
        "Small_World_80": lambda: remove_low_connectivity_vertices(small_world_graph(80)),
        "Small_World_100": lambda: remove_low_connectivity_vertices(small_world_graph(100)),
        "Small_World_120": lambda: remove_low_connectivity_vertices(small_world_graph(120)),
        "Preferential_Attachment_80": lambda: remove_low_connectivity_vertices(preferential_attachment_graph(80)),
        "Preferential_Attachment_100": lambda: remove_low_connectivity_vertices(preferential_attachment_graph(100)),
        "Preferential_Attachment_120": lambda: remove_low_connectivity_vertices(preferential_attachment_graph(120))      
    }

    lambda_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    # Run experiment
    for _ in range(sample_size):
        topology = topology_factories[topology_name]()
        origin, destination = random.choice(sample_non_edges(topology, 5))
        # Adds random failures
        failed_edges = []
        for edge in topology.edges():
            if random.random() < p:
                failed_edges.append(edge)

        for lambda_value in lambda_values:
            algorithm = MaxFlowRouting(lambda_value)
            network = Network.from_networkx_graph(topology)
            engine = SimulationEngine(network=network, allow_backtracking=True, debug_print=False)

            # Adds random failures
            for edge in failed_edges:
                engine.add_edge_failure((edge[0], edge[1]))

            success, _ = engine.simulate_routing(
                origin, destination, algorithm,
                f"{origin}-{destination}",
                filename
            )
            if not success:
                print(f"Routing failed for: {origin},{destination}")
                continue

if __name__ == "__main__":
    # Real Topologies
    run_experiment("ChinaNet", "results_optimization/chinanet.csv", 10000)
    print("ChinaNet", flush=True)
    run_experiment("Geant", "results_optimization/geant.csv", 10000)
    print("Geant", flush=True)
    run_experiment("Internet2", "results_optimization/internet2.csv", 10000)
    print("Internet2", flush=True)
    run_experiment("RNP", "results_optimization/rnp.csv", 10000)
    print("RNP", flush=True)

    # Random Graphs with varied connectivity
    run_experiment("Random_80_0.1", "results_optimization/random_80_01.csv", 10000)
    print("Random 80 0.1", flush=True)
    run_experiment("Random_80_0.2", "results_optimization/random_80_02.csv", 10000)
    print("Random 80 0.2", flush=True)
    run_experiment("Random_80_0.3", "results_optimization/random_80_03.csv", 10000)
    print("Random 80 0.3", flush=True)
    run_experiment("Random_100_0.1", "results_optimization/random_100_01.csv", 10000)
    print("Random 100 0.1", flush=True)
    run_experiment("Random_100_0.2", "results_optimization/random_100_02.csv", 10000)
    print("Random 100 0.2", flush=True)
    run_experiment("Random_100_0.3", "results_optimization/random_100_03.csv", 10000)
    print("Random 100 0.3", flush=True)
    run_experiment("Random_120_0.1", "results_optimization/random_120_01.csv", 10000)
    print("Random 120 0.1", flush=True)
    run_experiment("Random_120_0.2", "results_optimization/random_120_02.csv", 10000)
    print("Random 120 0.2", flush=True)
    run_experiment("Random_120_0.3", "results_optimization/random_120_03.csv", 10000)
    print("Random 120 0.3", flush=True)

    # Small World Graphs
    run_experiment("Small_World_80", "results_optimization/small_world_80.csv", 10000)
    print("Small 80", flush=True)
    run_experiment("Small_World_100", "results_optimization/small_world_100.csv", 10000)
    print("Small 100", flush=True)
    run_experiment("Small_World_120", "results_optimization/small_world_120.csv", 10000)
    print("Small 120", flush=True)

    # Preferential Attachment Graphs
    run_experiment("Preferential_Attachment_80", "results_optimization/pref_att_80.csv", 10000)
    print("Preferential 80", flush=True)
    run_experiment("Preferential_Attachment_100", "results_optimization/pref_att_100.csv", 10000)
    print("Preferential 100", flush=True)
    run_experiment("Preferential_Attachment_120", "results_optimization/pref_att_120.csv", 10000)
    print("Preferential 120", flush=True)