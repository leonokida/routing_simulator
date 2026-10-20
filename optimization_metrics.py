import networkx as nx
from routing_sim.packet import Packet
from routing_sim.routing_algorithms.interface import RoutingAlgorithm
import os
import csv

def compute_optimization_metrics(
    file_path: str, 
    experiment_name: str, 
    algorithm: RoutingAlgorithm, 
    packet: Packet, 
    global_topology: nx.Graph, 
    failed_edges: set
):
    route = packet.final_route
    if not route or route[-1] != packet.destination:
        return

    route_length = len(route) - 1
    
    graph_with_failures = global_topology.copy()
    for u, v in failed_edges:
        if graph_with_failures.has_edge(u, v):
            graph_with_failures.remove_edge(u, v)
    
    min_possible_dist = nx.shortest_path_length(graph_with_failures, packet.origin, packet.destination)
    stretch = route_length - min_possible_dist

    headers = [
        "Experiment_Name",
        "Algorithm",
        "Route_Length",
        "Stretch",
        "Num_Vertices", 
        "Num_Edges", 
        "Edge_Connectivity",
        "Diameter", 
        "Avg_Degree",
        "Avg_Shortest_Path_Length"
    ]
    
    row = {
        "Experiment_Name": experiment_name,
        "Algorithm": algorithm.name,
        "Route_Length": route_length,
        "Stretch": stretch,
        "Num_Vertices": global_topology.number_of_nodes(),
        "Num_Edges": global_topology.number_of_edges(),
        "Edge_Connectivity": nx.edge_connectivity(global_topology),
        "Diameter": nx.diameter(global_topology),
        "Avg_Degree": 2 * global_topology.number_of_edges() / float(global_topology.number_of_nodes()),
        "Avg_Shortest_Path_Length": nx.average_shortest_path_length(global_topology)
    }

    file_exists = os.path.isfile(file_path) and os.path.getsize(file_path) > 0

    with open(file_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)