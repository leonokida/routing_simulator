# Tools for logging routing messages and calculating path metrics
# Author: Leon Okida
# Last modification: 01/27/2026

import networkx as nx
from routing_sim.packet import Packet
from routing_sim.routing_algorithms.interface import RoutingAlgorithm
import os
import csv

class RoutingMetrics:
    def __init__(self, debug_print: bool = True):
        self.logs = []
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
        log_entry = f"[Router {router_name}]: routing through {failed_next_hop} failed. Trying next option."
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
    
    @staticmethod
    def _get_number_of_paths_for_node(graph: nx.Graph, source: str | int, dest: str | int):
        # Computes the number of paths from source to dest
        try:
            return nx.maximum_flow_value(graph, source, dest, capacity='capacity')
        except nx.NetworkXNoPath:
            return 0
        except Exception:
            return 0

    def compute_final_metrics(self, packet: Packet, global_topology: nx.Graph):
        # Computes and prints final metrics for the successful route.
        route = packet.path
        if not route or route[-1] != packet.destination:
            print("\n--- Metrics Skipped: Routing failed or incomplete ---")
            return

        print("\n" + "="*40)
        print("SIMULATION METRICS")
        print("="*40)

        # 1. Length of the route
        route_length = len(route) - 1
        print(f"1. Route Length (Hops): {route_length}")

        # 2. Sum of degrees of the vertices in the route
        total_degree = sum(global_topology.degree(node) for node in route)
        print(f"2. Sum of Vertex Degrees: {total_degree}")

        # 3. Average alternate path neighbors
        dest = route[-1]
        temp_graph = global_topology.copy()

        # Remove edges in the used route (simulating failure of the primary path)
        for i in range(len(route) - 1):
            u = route[i]
            v = route[i+1]
            if temp_graph.has_edge(u, v):
                temp_graph.remove_edge(u, v)

        total_alternate_paths = 0
        nodes_to_check = route[1:-1] # Exclude source and destination

        if nodes_to_check:
            # We check max edge-disjoint paths (flow value with capacity=1)
            for node in nodes_to_check:
                alternate_paths = self._get_number_of_paths_for_node(temp_graph, node, dest)
                total_alternate_paths += alternate_paths
            
            avg_alternate_paths = total_alternate_paths / len(nodes_to_check)
            print(f"3. Avg. Alternate Routes: {avg_alternate_paths:.3f}")
        else:
            print("3. Avg. Alternate Routes: N/A (Route too short)")
        
        print(f"Backtracks Performed: {self.backtrack_counter}")
        print("="*40)
        
    def save_metrics_to_csv(self, file_path: str, experiment_name: str, algorithm: RoutingAlgorithm, packet: Packet, global_topology: nx.Graph):
        """
        Computes metrics and saves them to a CSV file, including an experiment identifier.
        """
        route = packet.path
        if not route or route[-1] != packet.destination:
            return

        # 1. Metric Calculations
        route_length = len(route) - 1
        total_degree = sum(global_topology.degree(node) for node in route)
        
        # Calculate Average Alternate Routes (disjoint paths to destination)
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
                # Using the existing helper method
                total_alternate_paths += self._get_number_of_paths_for_node(temp_graph, node, dest)
            avg_alternate_paths = total_alternate_paths / len(nodes_to_check)

        # 2. CSV Configuration
        headers = [
            "Experiment_Name",
            "Algorithm", 
            "Route_Length", 
            "Total_Degree", 
            "Avg_Alternate_Routes", 
            "Backtracks"
        ]
        
        row = {
            "Experiment_Name": experiment_name,
            "Algorithm": algorithm.name,
            "Route_Length": route_length,
            "Total_Degree": total_degree,
            "Avg_Alternate_Routes": round(avg_alternate_paths, 3),
            "Backtracks": self.backtrack_counter
        }

        # 3. File Writing Logic
        # Check if file exists and has content to determine if headers are needed
        file_exists = os.path.isfile(file_path) and os.path.getsize(file_path) > 0

        with open(file_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)