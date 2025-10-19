# The class that represents a Network of routers
# Author: Leon Okida
# Last modification: 10/19/2025

import networkx as nx
from routing_sim.router import Router
from routing_sim.routing_algorithms.interface import RoutingAlgorithm

class Network:
    def __init__(self):
        self.routers = {} 
        self.topology = nx.Graph()

    def add_router(self, router_name: str | int, algorithm: RoutingAlgorithm = None):
        # Adds a router with a routing algorithm
        if router_name not in self.routers:
            new_router = Router(name=router_name, algorithm=algorithm)
            self.routers[router_name] = new_router
            self.topology.add_node(router_name)
        elif algorithm is not None:
             self.routers[router_name].routing_algorithm = algorithm 
        return self.routers[router_name]

    def add_link(self, router_a_name: str | int, router_b_name: str | int, weight: int = 1, capacity: int = 1):
        # Adds a link between two routers
        self.topology.add_edge(router_a_name, router_b_name, weight=weight, capacity=capacity)
    
    @classmethod
    def from_networkx_graph(cls, graph: nx.Graph, algorithm_instance: str | int):
        # Initializes a network from a graph representing a topology
        new_network = cls() 
        
        for router_name in graph.nodes:
            # Adds the router with the assigned routing algorithm
            new_network.add_router(router_name, algorithm_instance) 
            
        for u, v, data in graph.edges(data=True):
            weight = data.get('weight', 1) 
            capacity = data.get('capacity', 1) 
            new_network.add_link(u, v, weight=weight, capacity=capacity)
            
        new_network.pre_calculate_arborescences()
        return new_network

    def pre_calculate_arborescences(self):
        # Computes the arborescence packing
        connectivity_c = nx.edge_connectivity(self.topology)
        arborescence_packing = {}

        # Iterate over every possible destination d
        for d in self.topology.nodes:
            d_arborescences = {}
            # Iterate over every possible source s (which is every node except d)
            for s in self.topology.nodes:
                if s == d:
                    continue

                # Find the required number of edge-disjoint paths (SEDPs)
                try:
                    # Use NetworkX's flow capabilities to find edge-disjoint paths
                    # nx.edge_disjoint_paths returns an iterator of paths
                    paths_iterator = nx.edge_disjoint_paths(self.topology, s, d)
                    
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
    