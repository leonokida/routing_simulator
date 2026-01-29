# The routing algorithm based on Dijkstra's algorithm
# Author: Leon Okida
# Last modification: 01/27/2026

import networkx as nx
from routing_sim.routing_algorithms.interface import RoutingAlgorithm
import routing_sim.routing_algorithms.utils as utils

class DijsktraRouting(RoutingAlgorithm):
    def __init__(self):
        super().__init__("Algorithm based on Dijkstra's")

    def calculate_next_hop(self, source: str | int, dest: str | int, global_topology: nx.Graph, visited_names: set) -> list:
        # Calculates and returns a list of next hops sorted by shortest path length (ascending)
        scored_neighbors = []
        
        # Considers only unvisited neighbors that are not the source itself
        neighbors = [n for n in global_topology.neighbors(source) if n != source and n not in visited_names]
        
        if not neighbors:
            return []

        # Removes the source vertex from the graph used in the computation
        temp_graph = global_topology.copy()
        temp_graph.remove_node(source)

        for neighbor in neighbors:
            score = utils.get_shortest_path_length(neighbor, dest, temp_graph)
            
            # Only include neighbors that actually have a path to the destination
            if score != float('inf'):
                scored_neighbors.append((neighbor, score))
        
        # Sorts by distance in ascending order
        scored_neighbors.sort(key=lambda x: x[1])        
        return [hop[0] for hop in scored_neighbors]

    def switch_arborescence(self) -> None:
        raise NotImplementedError