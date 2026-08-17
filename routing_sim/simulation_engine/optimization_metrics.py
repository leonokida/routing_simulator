# Tools for logging routing messages and calculating path metrics
# Author: Leon Okida
# Last modification: 08/17/2026

from routing_sim.simulation_engine.metrics import Metrics
import networkx as nx
from routing_sim.packet import Packet
from routing_sim.routing_algorithms.interface import RoutingAlgorithm
import os
import csv

class OptimizationMetrics(Metrics):
    def __init__(self, debug_print=True):
        self.logs = []
        self.found_failures = []
        self.backtrack_counter = 0
        self.debug_print = debug_print

    def log_forwarding(self, router_name: str | int, next_hop: str | int):
        # Logs a hop
        log_entry = f"[Router {router_name}]: forwarding to {next_hop}."
        self.logs.append(log_entry)
        if self.debug_print:
            print(log_entry)

    def log_failure(self, router_name: str | int, failed_next_hop: str | int):
        # Logs the impossibility of routing through a router
        log_entry = f"[Router {router_name}]: forwarding to {failed_next_hop} failed. Activating backup route."
        self.found_failures.append((router_name, failed_next_hop))
        self.logs.append(log_entry)
        if self.debug_print:
            print(log_entry)

    def log_backtrack(self, router_name: str | int, previous_router: str | int):
        # Logs a backtrack event
        self.backtrack_counter += 1
        if previous_router != "":
            log_entry = f"[Router {router_name}]: BACKTRACK! All options depleted. Returning to {previous_router}."
            self.logs.append(log_entry)
            if self.debug_print:
                print(log_entry)

    def log_success(self, final_route: list):
        # Logs the routing success
        log_entry = f"ROUTING SUCCESSFUL! Final Route: {final_route}"
        self.logs.append(log_entry)
        if self.debug_print:
            print(log_entry)

    def log_hop_history(self, hop_history: list):
        log_entry = f"Full hop history: {hop_history}"
        self.logs.append(log_entry)
        if self.debug_print:
            print(log_entry)
        
    def compute_metrics(
        self, 
        file_path: str, 
        experiment_name: str, 
        algorithm: RoutingAlgorithm, 
        packet: Packet, 
        global_topology: nx.Graph, 
        failed_edges: set
    ):
        # Computes metrics and saves them to a CSV file, including an experiment identifier.
        route = packet.final_route
        if not route or route[-1] != packet.destination:
            return

        route_length = len(route) - 1
        # Calculate stretch
        graph_with_failures = global_topology.copy()
        for u, v in failed_edges:
            if graph_with_failures.has_edge(u, v):
                graph_with_failures.remove_edge(u, v)
        
        min_possible_dist = nx.shortest_path_length(graph_with_failures, packet.origin, packet.destination)
        stretch = route_length - min_possible_dist

        # 2. CSV Configuration
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

        # 3. File Writing Logic
        # Check if file exists and has content to determine if headers are needed
        file_exists = os.path.isfile(file_path) and os.path.getsize(file_path) > 0

        with open(file_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)