# The arborecence-based routing algorithm, using a precomputed arborescence packing
# Author: Leon Okida
# Last modification: 10/19/2025

import networkx as nx
from routing_sim.routing_algorithms.interface import RoutingAlgorithm

class ArborescenceRouting(RoutingAlgorithm):
    def __init__(self):
        super().__init__("ArborescenceRouting")
        self.arborescence_packing = None

    def add_arborescence_packing(self, arborescence_packing: dict) -> None:
        # Loads the precomputed arborescence packing
        self.arborescence_packing = arborescence_packing

    def calculate_next_hop(self, source: str | int, dest: str | int, global_topology: nx.Graph, visited_names: set) -> tuple:      
        # Calculates the next hop based on the arborescences
        if dest not in self.arborescence_packing:
            return None, float('-inf')

        potential_next_hops = self.arborescence_packing.get(dest, {}).get(source, [])
        
        if not potential_next_hops:
            return None, float('-inf')
        # Iterates through arborescences to find a next hop
        for arbo_index in range(len(potential_next_hops)):
            next_hop = potential_next_hops[arbo_index]
            if next_hop not in visited_names:
                try:
                    edge_cost = global_topology[source][next_hop].get('weight', 1)
                    return next_hop, -edge_cost 
                except KeyError:
                    continue

        return None, float('-inf')