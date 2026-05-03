# Experiment comparing MaxFlowRouting, Arborescence Routing and the algorithm based on Dijkstra's
# Author: Leon Okida
# Last modification: 05/03/2026

from routing_sim.routing_algorithms.max_flow_routing import MaxFlowRouting
from routing_sim.routing_algorithms.dijkstra_routing import DijkstraRouting
from routing_sim.routing_algorithms.arborescence_routing import ArborescenceRouting
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

def run_experiment(topology_name: str, filename: str, sample_size: int = 30):
    # Factories to avoid reusing instances on more than one execution
    topology_factories = {
        "ChinaNet": lambda: remove_low_connectivity_vertices(read_graph("topologies/chinanet.txt")),
        "Geant": lambda: remove_low_connectivity_vertices(read_graph("topologies/geant.txt")),
        "Internet2": lambda: remove_low_connectivity_vertices(read_graph("topologies/internet2.txt")),
        "RNP": lambda: remove_low_connectivity_vertices(read_graph("topologies/rnp.txt")),
        "Random_100_0.3": lambda: random_graph(100, 0.3),
        "Random_100_0.5": lambda: random_graph(100, 0.5),
        "Random_100_0.7": lambda: random_graph(100, 0.7),
        "Random_150_0.3": lambda: random_graph(150, 0.3),
        "Random_150_0.5": lambda: random_graph(150, 0.5),
        "Random_150_0.7": lambda: random_graph(150, 0.7),
        "Random_200_0.3": lambda: random_graph(200, 0.3),
        "Random_200_0.5": lambda: random_graph(200, 0.5),
        "Random_200_0.7": lambda: random_graph(200, 0.7),
        "Small_World_100": lambda: small_world_graph(100),
        "Small_World_150": lambda: small_world_graph(150),
        "Small_World_200": lambda: small_world_graph(200),
        "Preferential_Attachment_100": lambda: preferential_attachment_graph(100),
        "Preferential_Attachment_150": lambda: preferential_attachment_graph(150),
        "Preferential_Attachment_200": lambda: preferential_attachment_graph(200)      
    }

    algorithm_factories = [
        lambda: DijkstraRouting(),
        lambda: MaxFlowRouting(0.2),
        lambda: MaxFlowRouting(0.5),
        lambda: MaxFlowRouting(0.8),
        lambda: ArborescenceRouting(),
    ]

    # Run experiment
    for _ in range(sample_size):
        topology = topology_factories[topology_name]()
        origin, destination = random.choice(sample_non_edges(topology, 5))

        for make_algorithm in algorithm_factories:
            algorithm = make_algorithm()
            network = Network.from_networkx_graph(topology)
            allow_backtracking = False if algorithm.name == "Arborescence Routing" else True
            engine = SimulationEngine(network=network, allow_backtracking=allow_backtracking, debug_print=False)

            # Routes without failure
            _, packet = engine.simulate_routing(
                origin, destination, algorithm,
                f"{origin}-{destination} without failures",
                filename
            )
            route = packet.final_route

            if route is None or len(route) < 3:
                print(f"Routing failed for: {origin},{destination}")
                continue

            # Routes with failure
            idx = random.randrange(len(route) - 1)
            edge_to_fail = (route[idx], route[idx + 1])
            engine.add_edge_failure(edge_to_fail)

            _, route = engine.simulate_routing(
                origin, destination, algorithm,
                f"{origin}-{destination} with failure on {edge_to_fail[0]}-{edge_to_fail[1]}",
                filename
            )
            route = packet.final_route

            if route is None or len(route) < 3:
                print(f"Routing failed for: {origin},{destination}")
                continue

if __name__ == "__main__":
    # Real Topologies
    run_experiment("ChinaNet", "results/chinanet.csv", 30)
    print("ChinaNet", flush=True)
    run_experiment("Geant", "results/geant.csv", 30)
    print("Geant", flush=True)
    run_experiment("Internet2", "results/internet2.csv", 30)
    print("Internet2", flush=True)
    run_experiment("RNP", "results/rnp.csv", 30)
    print("RNP", flush=True)

    # Random Graphs with varied connectivity
    run_experiment("Random_100_0.3", "results/random_100_03.csv", 30)
    print("Random 100 0.3", flush=True)
    run_experiment("Random_100_0.5", "results/random_100_05.csv", 30)
    print("Random 100 0.5", flush=True)
    run_experiment("Random_100_0.7", "results/random_100_07.csv", 30)
    print("Random 100 0.7", flush=True)
    run_experiment("Random_150_0.3", "results/random_150_03.csv", 30)
    print("Random 150 0.3", flush=True)
    run_experiment("Random_150_0.5", "results/random_150_05.csv", 30)
    print("Random 150 0.5", flush=True)
    run_experiment("Random_150_0.7", "results/random_150_07.csv", 30)
    print("Random 150 0.7", flush=True)
    run_experiment("Random_200_0.3", "results/random_200_03.csv", 30)
    print("Random 200 0.3", flush=True)
    run_experiment("Random_200_0.5", "results/random_200_05.csv", 30)
    print("Random 200 0.5", flush=True)
    run_experiment("Random_200_0.7", "results/random_200_07.csv", 30)
    print("Random 200 0.7", flush=True)

    # Small World Graphs
    run_experiment("Small_World_100", "results/small_world_100.csv", 30)
    print("Small 100", flush=True)
    run_experiment("Small_World_150", "results/small_world_150.csv", 30)
    print("Small 150", flush=True)
    run_experiment("Small_World_200", "results/small_world_200.csv", 30)
    print("Small 200", flush=True)

    # Preferential Attachment Graphs
    run_experiment("Preferential_Attachment_100", "results/pref_att_100.csv", 30)
    print("Preferential 100", flush=True)
    run_experiment("Preferential_Attachment_150", "results/pref_att_150.csv", 30)
    print("Preferential 150", flush=True)
    run_experiment("Preferential_Attachment_200", "results/pref_att_200.csv", 30)
    print("Preferential 200", flush=True)