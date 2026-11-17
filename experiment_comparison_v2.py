# Experiment comparing Dijkstra, MaxFlowRouting (with GNN-predicted lambda) and Arborescence Routing
# Author: Leon Okida
# Last modification: 11/14/2026

from routing_sim.routing_algorithms.max_flow_routing import MaxFlowRouting
from routing_sim.routing_algorithms.dijkstra_routing import DijkstraRouting
from routing_sim.routing_algorithms.arborescence_routing import ArborescenceRouting
from routing_sim.simulation_engine.simulation_engine import SimulationEngine
from comparison_metrics import compute_comparison_metrics
from routing_sim.packet import Packet
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

from machine_learning_optimization.model import LambdaPredictorGNN
import torch
import torch.nn as nn
from torch_geometric.data import Data

from tqdm import tqdm
import concurrent.futures

def from_networkx_to_pyg(G: nx.Graph) -> Data:
    # Converts to the format accepted by PyTorch
    mapping = {node: i for i, node in enumerate(G.nodes())}
    G_reindexed = nx.relabel_nodes(G, mapping)
    
    edge_index = torch.tensor(list(G_reindexed.edges()), dtype=torch.long).t().contiguous()
    edge_index = torch.cat([edge_index, edge_index.flip(0)], dim=1)
    
    degrees = [val for _, val in G_reindexed.degree()]
    max_deg = max(degrees) if degrees else 1.0
    x = torch.tensor([[d / max_deg] for d in degrees], dtype=torch.float)
    
    return Data(x=x, edge_index=edge_index)

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
        "Random_80_0.1": lambda: remove_low_connectivity_vertices(random_graph(80, 0.1)),
        "Random_80_0.2": lambda: remove_low_connectivity_vertices(random_graph(80, 0.2)),
        "Random_80_0.3": lambda: remove_low_connectivity_vertices(random_graph(80, 0.3)),
        "Random_90_0.1": lambda: remove_low_connectivity_vertices(random_graph(90, 0.1)),
        "Random_90_0.2": lambda: remove_low_connectivity_vertices(random_graph(90, 0.2)),
        "Random_90_0.3": lambda: remove_low_connectivity_vertices(random_graph(90, 0.3)),
        "Random_100_0.1": lambda: remove_low_connectivity_vertices(random_graph(100, 0.1)),
        "Random_100_0.2": lambda: remove_low_connectivity_vertices(random_graph(100, 0.2)),
        "Random_100_0.3": lambda: remove_low_connectivity_vertices(random_graph(100, 0.3)),
        "Random_110_0.1": lambda: remove_low_connectivity_vertices(random_graph(110, 0.1)),
        "Random_110_0.2": lambda: remove_low_connectivity_vertices(random_graph(110, 0.2)),
        "Random_110_0.3": lambda: remove_low_connectivity_vertices(random_graph(110, 0.3)),
        "Random_120_0.1": lambda: remove_low_connectivity_vertices(random_graph(120, 0.1)),
        "Random_120_0.2": lambda: remove_low_connectivity_vertices(random_graph(120, 0.2)),
        "Random_120_0.3": lambda: remove_low_connectivity_vertices(random_graph(120, 0.3)),
        "Small_World_80": lambda: remove_low_connectivity_vertices(small_world_graph(80)),
        "Small_World_90": lambda: remove_low_connectivity_vertices(small_world_graph(90)),
        "Small_World_100": lambda: remove_low_connectivity_vertices(small_world_graph(100)),
        "Small_World_110": lambda: remove_low_connectivity_vertices(small_world_graph(110)),
        "Small_World_120": lambda: remove_low_connectivity_vertices(small_world_graph(120)),
        "Preferential_Attachment_80": lambda: remove_low_connectivity_vertices(preferential_attachment_graph(80)),
        "Preferential_Attachment_90": lambda: remove_low_connectivity_vertices(preferential_attachment_graph(90)),
        "Preferential_Attachment_100": lambda: remove_low_connectivity_vertices(preferential_attachment_graph(100)),
        "Preferential_Attachment_110": lambda: remove_low_connectivity_vertices(preferential_attachment_graph(110)),
        "Preferential_Attachment_120": lambda: remove_low_connectivity_vertices(preferential_attachment_graph(120))      
    }

    # Loads the pretrained GNN
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    gnn_model = LambdaPredictorGNN(in_channels=1, hidden_channels=64).to(device)
    gnn_model.load_state_dict(torch.load("machine_learning_optimization/model/best_lambda_predictor_gnn.pth", weights_only=True))
    gnn_model.eval()

    # Run experiment
    for _ in range(sample_size):
        topology = topology_factories[topology_name]()
        
        # Predicts optimal lambda for MaxFlowRouting considering the topology
        pyg_data = from_networkx_to_pyg(topology).to(device)
        pyg_data.batch = torch.zeros(pyg_data.num_nodes, dtype=torch.long, device=device)
        with torch.no_grad():
            predicted_lambda = gnn_model(pyg_data.x, pyg_data.edge_index, pyg_data.batch).item()

        # Define os algoritmos usando o lambda dinâmico predito para o MaxFlowRouting
        algorithm_factories = [
            lambda: DijkstraRouting(),
            lambda: MaxFlowRouting(lambda_val=predicted_lambda),
            lambda: ArborescenceRouting(),
        ]

        origin, destination = random.choice(sample_non_edges(topology, 5))

        for make_algorithm in algorithm_factories:
            algorithm = make_algorithm()
            network = Network.from_networkx_graph(topology)
            allow_backtracking = False if algorithm.name == "Arborescence Routing" else True
            engine = SimulationEngine(network=network, allow_backtracking=allow_backtracking)

            # Routes without failure
            packet_without_failure = Packet(origin_name=origin, destination_name=destination)
            route = engine.simulate_routing(packet_without_failure, algorithm)

            if route is None:
                continue

            compute_comparison_metrics(
                file_path=filename,
                experiment_name=f"{origin}-{destination} without failures",
                algorithm=algorithm,
                packet=packet_without_failure,
                global_topology=network.topology,
                failed_edges=engine.failed_edges
            )

            # Routes with failure
            idx = random.randrange(len(route) - 1)
            edge_to_fail = (route[idx], route[idx + 1])
            engine.add_edge_failure(edge_to_fail)

            packet_with_failure = Packet(origin_name=origin, destination_name=destination)
            route = engine.simulate_routing(packet_with_failure, algorithm)

            if route is None or len(route) < 3:
                continue

            compute_comparison_metrics(
                file_path=filename,
                experiment_name=f"{origin}-{destination} with failure on {edge_to_fail[0]}-{edge_to_fail[1]}",
                algorithm=algorithm,
                packet=packet_with_failure,
                global_topology=network.topology,
                failed_edges=engine.failed_edges
            )

def _run_experiment_wrapper(args):
    return run_experiment(*args)

if __name__ == "__main__":
    experiments = [
        ("ChinaNet", "results_comparison_v2/chinanet.csv", 30),
        ("Geant", "results_comparison_v2/geant.csv", 30),
        ("Internet2", "results_comparison_v2/internet2.csv", 30),
        ("RNP", "results_comparison_v2/rnp.csv", 30),
        ("Random_80_0.1", "results_comparison_v2/random_80_01.csv", 30),
        ("Random_80_0.2", "results_comparison_v2/random_80_02.csv", 30),
        ("Random_80_0.3", "results_comparison_v2/random_80_03.csv", 30),
        ("Random_90_0.1", "results_comparison_v2/random_90_01.csv", 30),
        ("Random_90_0.2", "results_comparison_v2/random_90_02.csv", 30),
        ("Random_90_0.3", "results_comparison_v2/random_90_03.csv", 30),
        ("Random_100_0.1", "results_comparison_v2/random_100_01.csv", 30),
        ("Random_100_0.2", "results_comparison_v2/random_100_02.csv", 30),
        ("Random_100_0.3", "results_comparison_v2/random_100_03.csv", 30),
        ("Random_110_0.1", "results_comparison_v2/random_110_01.csv", 30),
        ("Random_110_0.2", "results_comparison_v2/random_110_02.csv", 30),
        ("Random_110_0.3", "results_comparison_v2/random_110_03.csv", 30),
        ("Random_120_0.1", "results_comparison_v2/random_120_01.csv", 30),
        ("Random_120_0.2", "results_comparison_v2/random_120_02.csv", 30),
        ("Random_120_0.3", "results_comparison_v2/random_120_03.csv", 30),
        ("Small_World_80", "results_comparison_v2/small_world_80.csv", 30),
        ("Small_World_90", "results_comparison_v2/small_world_90.csv", 30),
        ("Small_World_100", "results_comparison_v2/small_world_100.csv", 30),
        ("Small_World_110", "results_comparison_v2/small_world_110.csv", 30),
        ("Small_World_120", "results_comparison_v2/small_world_120.csv", 30),
        ("Preferential_Attachment_80", "results_comparison_v2/pref_att_80.csv", 30),
        ("Preferential_Attachment_90", "results_comparison_v2/pref_att_90.csv", 30),
        ("Preferential_Attachment_100", "results_comparison_v2/pref_att_100.csv", 30),
        ("Preferential_Attachment_110", "results_comparison_v2/pref_att_110.csv", 30),
        ("Preferential_Attachment_120", "results_comparison_v2/pref_att_120.csv", 30),
    ]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        list(tqdm(
            executor.map(_run_experiment_wrapper, experiments),
            total=len(experiments),
            desc="Running Experiments"
        ))