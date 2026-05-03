# The MaxFlowRouting algorithm
# Author: Leon Okida
# Last modification: 05/03/2026

import networkx as nx
from routing_sim.routing_algorithms.interface import RoutingAlgorithm
import routing_sim.routing_algorithms.utils as utils

class MaxFlowRouting(RoutingAlgorithm):
    def __init__(self, lambda_val: float = 0.8):
        super().__init__(f"MaxFlowRouting with lambda={lambda_val}")
        self.weight_mf = lambda_val
        self.weight_sp = (1 - lambda_val) * -1
    
    def initial_setup(self, source, dest, global_topology):
        self.routing = dict()

    def compute_routes(self, source: str | int, dest: str | int, global_topology: nx.Graph) -> None:
        if source not in self.routing:
            self.routing[source] = dict()
            # Orders neighbors by score (descending)
            scored_neighbors = []
            
            neighbors = [n for n in global_topology.neighbors(source) if n != source]
            if not neighbors:
                return []

            g_prime = global_topology.copy()
            g_prime.remove_node(source)

            for neighbor in neighbors:
                sp_score = utils.get_shortest_path_length(neighbor, dest, g_prime)
                if sp_score == float('inf'):
                    continue 

                mf_score = utils.get_max_flow_value(neighbor, dest, g_prime)
                
                # Γ = (λ * MF) + (-(1-λ) * SP)
                score = (self.weight_mf * mf_score) + (self.weight_sp * sp_score)
                scored_neighbors.append((neighbor, score))

            # Sort the list of tuples by score in descending order
            scored_neighbors.sort(key=lambda x: x[1], reverse=True)
            self.routing[source]["index"] = 0
            self.routing[source]["neighbors"] = [neighbor[0] for neighbor in scored_neighbors]
    
    def calculate_next_hop(self, source: str | int, dest: str | int, global_topology: nx.Graph, visited_names: set) -> str | int:
        self.compute_routes(source, dest, global_topology)
        index = self.routing[source]["index"]
        if index < len(self.routing[source]["neighbors"]):
            for neighbor in self.routing[source]["neighbors"][index:]:
                if neighbor not in visited_names:
                    return neighbor
        return None
    
    def handle_failure(self, source, dest):
        self.routing[source]["index"] += 1
