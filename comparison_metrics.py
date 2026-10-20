import networkx as nx
from routing_sim.packet import Packet
from routing_sim.routing_algorithms.interface import RoutingAlgorithm
import os
import csv

def _get_number_of_paths_for_node(graph: nx.Graph, source: str | int, dest: str | int):
    try:
        return nx.maximum_flow_value(graph, source, dest, capacity='capacity')
    except nx.NetworkXNoPath:
        return 0
    except Exception:
        return 0

def compute_comparison_metrics(
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
    total_degree = sum(global_topology.degree(node) for node in route)
    total_hops = len(packet.hop_history) - 1
    
    dest = route[-1]
    temp_graph = global_topology.copy()
    for i in range(len(route) - 1):
        u, v = route[i], route[i+1]
        if temp_graph.has_edge(u, v):
            temp_graph.remove_edge(u, v)

    total_alternate_paths = 0
    nodes_to_check = route[1:-1]
    avg_alternate_paths = 0
    if nodes_to_check:
        for node in nodes_to_check:
            total_alternate_paths += _get_number_of_paths_for_node(temp_graph, node, dest)
        avg_alternate_paths = total_alternate_paths / len(nodes_to_check)

    graph_with_failures = global_topology.copy()
    for u, v in failed_edges:
        if graph_with_failures.has_edge(u, v):
            graph_with_failures.remove_edge(u, v)
    
    min_possible_dist = nx.shortest_path_length(graph_with_failures, packet.origin, packet.destination)
    stretch = route_length - min_possible_dist
    stretch_ratio = route_length / min_possible_dist if min_possible_dist > 0 else 1.0

    headers = [
        "Experiment_Name",
        "Algorithm", 
        "Route_Length", 
        "Total_Hops",
        "Total_Degree", 
        "Avg_Alternate_Routes", 
        "Backtracks",
        "Stretch",
        "Stretch_Ratio"
    ]
    
    row = {
        "Experiment_Name": experiment_name,
        "Algorithm": algorithm.name,
        "Route_Length": route_length,
        "Total_Hops": total_hops,
        "Total_Degree": total_degree,
        "Avg_Alternate_Routes": round(avg_alternate_paths, 3),
        "Backtracks": packet.backtrack_count,
        "Stretch": stretch,
        "Stretch_Ratio": stretch_ratio
    }

    file_exists = os.path.isfile(file_path) and os.path.getsize(file_path) > 0

    with open(file_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)