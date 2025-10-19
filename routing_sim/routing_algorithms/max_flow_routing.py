# The MaxFlowRouting algorithm
# Author: Leon Okida
# Last modification: 10/19/2025

import networkx as nx
from routing_sim.routing_algorithms.interface import RoutingAlgorithm
import routing_sim.routing_algorithms.utils as utils

class MaxFlowRouting(RoutingAlgorithm):
    def __init__(self, lambda_val: float = 0.8):
        super().__init__("MaxFlowRouting")
        self.weight_mf = lambda_val
        self.weight_sp = (1 - lambda_val) * -1

    def calculate_next_hop(self, source: str | int, dest: str | int, global_topology: nx.Graph, visited_names: set) -> tuple:
        # Calculates the next hop using shortest path and max flow criteria
        best_score = float('-inf')
        best_next_hop = None
        
        # Excludes graphs that were already visited
        neighbors = [n for n in global_topology.neighbors(source) if n != source and n not in visited_names]
        if not neighbors:
            return None, float('-inf')

        # Removes the source vertex from the graph used in the computation
        temp_graph = global_topology.copy()
        temp_graph.remove_node(source)

        for neighbor in neighbors:
            # Computes shortest path
            sp_score = utils.get_shortest_path_length(neighbor, dest, temp_graph)
            if sp_score == float('inf'):
                continue 

            # Computes Max Flow
            mf_score = utils.get_max_flow_value(neighbor, dest, temp_graph)
            
            # Γ = (λ * MF) + (-(1-λ) * SP)
            score = (self.weight_mf * mf_score) + (self.weight_sp * sp_score)
            
            if score > best_score:
                best_score = score
                best_next_hop = neighbor

        return best_next_hop, best_score