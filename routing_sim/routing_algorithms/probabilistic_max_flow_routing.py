# The probabilistic version of the MaxFlowRouting algorithm
# Author: Leon Okida
# Last modification: 01/28/2026

import networkx as nx
from routing_sim.routing_algorithms.interface import RoutingAlgorithm
import routing_sim.routing_algorithms.utils as utils

class ProbabilisticMaxFlowRouting(RoutingAlgorithm):
    def __init__(self, lambda_val: float = 0.5, p: float = 0.1):
        super().__init__(f"Probabilistic MaxFlowRouting with lambda={lambda_val} and p={p}")
        self.lambda_val = lambda_val
        self.p = p

    # Calculates the expected minimum cost of backtracks with failures occurring with a probability of p
    def _expected_minimum_backtrack_cost(self, sp_score: int):
        cost = 0
        for i in range(0, sp_score + 1):
            cost += i * ((1 - self.p) ** i) * self.p
        return cost

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
            cost = self._expected_minimum_backtrack_cost(sp_score)
            
            # Γ = MF - (λ * C)
            score = mf_score - (self.lambda_val * cost)
            scored_neighbors.append((neighbor, score))

        # Sort the list of tuples by score in descending order
        scored_neighbors.sort(key=lambda x: x[1], reverse=True)
        return [hop[0] for hop in scored_neighbors]
    
    def switch_arborescence(self) -> None:
        raise NotImplementedError