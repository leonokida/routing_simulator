# The MaxFlowRouting algorithm
# Author: Leon Okida
# Last modification: 10/27/2025

import networkx as nx
from routing_sim.routing_algorithms.interface import RoutingAlgorithm
import routing_sim.routing_algorithms.utils as utils

class MaxFlowRouting(RoutingAlgorithm):
    def __init__(self, lambda_val: float = 0.8):
        super().__init__(f"MaxFlowRouting with lambda={lambda_val}")
        self.weight_mf = lambda_val
        self.weight_sp = (1 - lambda_val) * -1

    def calculate_next_hop(self, source: str | int, dest: str | int, global_topology: nx.Graph, visited_names: set) -> list:
        # Calculates and returns a list of next hops sorted by score (descending)
        scored_neighbors = []
        
        neighbors = [n for n in global_topology.neighbors(source) if n != source and n not in visited_names]
        if not neighbors:
            return []

        temp_graph = global_topology.copy()
        temp_graph.remove_node(source)

        for neighbor in neighbors:
            sp_score = utils.get_shortest_path_length(neighbor, dest, temp_graph)
            if sp_score == float('inf'):
                continue 

            mf_score = utils.get_max_flow_value(neighbor, dest, temp_graph)
            
            # Γ = (λ * MF) + (-(1-λ) * SP)
            score = (self.weight_mf * mf_score) + (self.weight_sp * sp_score)
            scored_neighbors.append((neighbor, score))

        # Sort the list of tuples by score in descending order
        scored_neighbors.sort(key=lambda x: x[1], reverse=True)
        return [hop[0] for hop in scored_neighbors]
    
    def switch_arborescence(self) -> None:
        raise NotImplementedError