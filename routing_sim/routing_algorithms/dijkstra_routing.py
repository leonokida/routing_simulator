# The routing algorithm based on Dijkstra's algorithm
# Author: Leon Okida
# Last modification: 10/19/2025

import networkx as nx
from routing_sim.routing_algorithms.interface import RoutingAlgorithm
import routing_sim.routing_algorithms.utils as utils

class DijsktraRouting(RoutingAlgorithm):
    def __init__(self):
        super().__init__("ShortestPath")

    def calculate_next_hop(self, source: str | int, dest: str | int, global_topology: nx.Graph, visited_names: set) -> tuple:
        # Calculates the next hop based on the shortest path from source to dest
        best_score = float('inf')
        best_next_hop = None
        
        # Considers only unvisited neighbors that are not the source itself
        neighbors = [n for n in global_topology.neighbors(source) if n != source and n not in visited_names]
        
        if not neighbors:
            return None, float('-inf')
        temp_graph = global_topology.copy()
        temp_graph.remove_node(source)

        # Finds the neighbor with the shortest path
        for neighbor in neighbors:
            score = utils.get_shortest_path_length(neighbor, dest, temp_graph)
            if score < best_score:
                best_score = score
                best_next_hop = neighbor
        
        if best_next_hop is not None and best_score != float('inf'):
            edge_cost = global_topology[source][best_next_hop].get('weight', 1)
            final_score = edge_cost + best_score
            return best_next_hop, final_score
        
        return None, float('-inf')
