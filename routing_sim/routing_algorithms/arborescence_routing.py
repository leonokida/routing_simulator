# The arborecence-based routing algorithm, using a precomputed arborescence packing
# Author: Leon Okida
# Last modification: 10/19/2025

import networkx as nx
from routing_sim.routing_algorithms.interface import RoutingAlgorithm

class ArborescenceRouting(RoutingAlgorithm):
    def __init__(self):
        super().__init__("ArborescenceRouting")
        self.arborescence_packing = None

    def compute_arborescence_packing(self, topology: nx.Graph) -> None:
        # Computes the arborescence packing
        connectivity_c = nx.edge_connectivity(topology)
        arborescence_packing = {}

        # Iterate over every possible destination d
        for d in topology.nodes:
            d_arborescences = {}
            # Iterate over every possible source s (which is every node except d)
            for s in topology.nodes:
                if s == d:
                    continue

                # Find the required number of edge-disjoint paths (SEDPs)
                try:
                    # Use NetworkX's flow capabilities to find edge-disjoint paths
                    # nx.edge_disjoint_paths returns an iterator of paths
                    paths_iterator = nx.edge_disjoint_paths(topology, s, d)
                    
                    # Take up to 'connectivity_c' paths
                    disjoint_paths = list(paths_iterator)[:connectivity_c]
                    
                    # Extract the next hop for each path
                    next_hops = []
                    for path in disjoint_paths:
                        if len(path) > 1:
                            next_hops.append(path[1]) # The second node in the path is the next hop
                    
                    d_arborescences[s] = next_hops
                    
                except nx.NetworkXNoPath:
                    # No path exists (shouldn't happen in a connected graph)
                    d_arborescences[s] = []
                
            arborescence_packing[d] = d_arborescences
            
        self.arborescence_packing = arborescence_packing # Store the computed structure

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