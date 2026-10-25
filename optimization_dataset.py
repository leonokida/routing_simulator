# Experiment that generates MaxFlowRouting data to train ML model
# Author: Leon Okida
# Last modification: 10/25/2026

import networkx as nx

from routing_sim.routing_algorithms.max_flow_routing import MaxFlowRouting
from routing_sim.simulation_engine.simulation_engine import SimulationEngine
from routing_sim.network import Network
from routing_sim.packet import Packet
from routing_sim.topology_generation import (
    read_graph, 
    remove_low_connectivity_vertices,
    random_graph,
    small_world_graph,
    preferential_attachment_graph
)

import random
import torch
from torch_geometric.data import Data
from concurrent.futures import ProcessPoolExecutor, as_completed

def get_non_neighbor_pairs(G: nx.Graph):
    nodes = list(G.nodes())
    pairs = set()
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            u, v = nodes[i], nodes[j]
            if not G.has_edge(u, v) and u != v:
                pairs.add((u, v)) # Avoids duplicates (u,v) and (v,u)
    return list(pairs)

def run_topology_optimization(topology: nx.Graph, lambda_values: list):
    pairs = get_non_neighbor_pairs(topology)
    if not pairs:
        return None
    
    lambda_avg_stretch = {l_val: [] for l_val in lambda_values}

    for u, v in pairs:
        for lambda_val in lambda_values:
            algorithm = MaxFlowRouting(lambda_val=lambda_val)
            network = Network.from_networkx_graph(topology)
            engine = SimulationEngine(network=network, allow_backtracking=True)
            
            packet = Packet(origin_name=u, destination_name=v)
            route = engine.simulate_routing(packet, algorithm)
            
            if not route or len(route) < 2:
                continue
            
            # Inserts failure in random edge
            idx = random.randrange(len(route) - 1)
            edge_to_fail = (route[idx], route[idx + 1])
            engine.add_edge_failure(edge_to_fail)
            
            # Simulates routing with failure
            packet_fail = Packet(origin_name=u, destination_name=v)
            route_fail = engine.simulate_routing(packet_fail, algorithm)
            
            if route_fail:
                # Computes additive stretch
                g_fail = topology.copy()
                g_fail.remove_edge(*edge_to_fail)
                try:
                    min_dist = nx.shortest_path_length(g_fail, u, v)
                    stretch = (len(route_fail) - 1) - min_dist
                    lambda_avg_stretch[lambda_val].append(stretch)
                except nx.NetworkXNoPath:
                    continue

    # Calculates each instance's average stretch and finds the optimal lambda
    best_lambda = None
    min_mean_stretch = float('inf')

    for l_val, stretches in lambda_avg_stretch.items():
        if stretches:
            mean_stretch = sum(stretches) / len(stretches)
            if mean_stretch < min_mean_stretch:
                min_mean_stretch = mean_stretch
                best_lambda = l_val

    return best_lambda

def _process_single_topology(args):
    idx, topo, lambda_values = args
    print(f"Processing topologia {idx}", flush=True)
    best_lambda = run_topology_optimization(topo, lambda_values)
    
    if best_lambda is not None:
        return from_networkx_with_target(topo, best_lambda)
    return None

def generate_pyg_dataset(num_random_topologies: int = 50):
    lambda_values = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
    dataset_list = []

    # 1. Internet topologies
    internet_topos = {
        #"ChinaNet": remove_low_connectivity_vertices(read_graph("topologies/chinanet.txt")),
        #"Geant": remove_low_connectivity_vertices(read_graph("topologies/geant.txt")),
        #"Internet2": remove_low_connectivity_vertices(read_graph("topologies/internet2.txt")),
        "RNP": remove_low_connectivity_vertices(read_graph("topologies/rnp.txt"))
    }

    all_topologies = list(internet_topos.values())

    # 2. Random topologies (N between 25 and 120)
    generators = [random_graph, small_world_graph, preferential_attachment_graph]
    for _ in range(num_random_topologies):
        size = random.randint(25, 120)
        gen_func = random.choice(generators)
        if gen_func == random_graph:
            topo = gen_func(size, connectivity=random.uniform(0.1, 0.3))
        else:
            topo = gen_func(size)
        all_topologies.append(remove_low_connectivity_vertices(topo))

    # 3. Paralelized processing
    tasks = [(i + 1, topo, lambda_values) for i, topo in enumerate(all_topologies)]
    
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(_process_single_topology, task) for task in tasks]
        
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                dataset_list.append(result)

    torch.save(dataset_list, "routing_optimization_dataset.pt")
    print("Dataset saved successfully in 'routing_optimization_dataset.pt'")

def from_networkx_with_target(G: nx.Graph, best_lambda: float) -> Data:
    mapping = {node: i for i, node in enumerate(G.nodes())}
    G_reindexed = nx.relabel_nodes(G, mapping)
    
    edge_index = torch.tensor(list(G_reindexed.edges()), dtype=torch.long).t().contiguous()
    edge_index = torch.cat([edge_index, edge_index.flip(0)], dim=1)
    
    degrees = [val for _, val in G_reindexed.degree()]
    max_deg = max(degrees) if degrees else 1.0
    x = torch.tensor([[d / max_deg] for d in degrees], dtype=torch.float)
    
    y = torch.tensor([best_lambda], dtype=torch.float)
    
    return Data(x=x, edge_index=edge_index, y=y)

if __name__ == "__main__":
    generate_pyg_dataset(num_random_topologies=0)