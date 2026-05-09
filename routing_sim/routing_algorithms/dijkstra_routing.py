# The routing algorithm based on Dijkstra's algorithm
# Author: Leon Okida
# Last modification: 05/09/2026

import networkx as nx
from routing_sim.routing_algorithms.interface import RoutingAlgorithm
import routing_sim.routing_algorithms.utils as utils

class DijkstraRouting(RoutingAlgorithm):
    def __init__(self):
        super().__init__(f"Algorithm based on Dijkstra's")
        self.routing = dict()
    
    def initial_setup(self, source, dest, global_topology):
        return

    def compute_routes(self, source: str | int, dest: str | int, global_topology: nx.Graph) -> None:
        if source not in self.routing:
            self.routing[source] = dict()
            # Calculates and returns a list of next hops sorted by the size of the shortest path (ascending)
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

                scored_neighbors.append((neighbor, sp_score))

            scored_neighbors.sort(key=lambda x: x[1])
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