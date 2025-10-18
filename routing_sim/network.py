import networkx as nx
from routing_sim.router import Router
from routing_sim.routing_algorithms.interface import RoutingAlgorithm

class Network:
    """Represents the entire network infrastructure."""
    def __init__(self):
        self.routers = {} 
        self.topology = nx.Graph()

    def add_router(self, router_name, algorithm=None): # <-- ALLOW algorithm to be optional
        """Adds a router and assigns an algorithm if provided."""
        if router_name not in self.routers:
            # We must pass the algorithm during Router creation
            new_router = Router(name=router_name, algorithm=algorithm)
            self.routers[router_name] = new_router
            self.topology.add_node(router_name)
        # Update existing router's algorithm if a new one is passed
        elif algorithm is not None:
             self.routers[router_name].routing_algorithm = algorithm 
        return self.routers[router_name]

    def add_link(self, router_a_name, router_b_name, weight=1, capacity=1):
        # We call add_router without an algorithm here, letting it default to None
        self.add_router(router_a_name)
        self.add_router(router_b_name)
        self.topology.add_edge(router_a_name, router_b_name, weight=weight, capacity=capacity)
    
    @classmethod
    def from_networkx_graph(cls, graph: nx.Graph, algorithm_instance):
        """
        Initializes a Network instance from an existing NetworkX graph and 
        assigns the given algorithm to all routers.
        """
        new_network = cls() 
        
        for router_name in graph.nodes:
            # Pass the algorithm instance to add_router
            new_network.add_router(router_name, algorithm_instance) 
            
        for u, v, data in graph.edges(data=True):
            weight = data.get('weight', 1) 
            capacity = data.get('capacity', 1) 
            # Note: add_link will call add_router again, but the router already exists
            new_network.add_link(u, v, weight=weight, capacity=capacity)
            
        new_network.pre_calculate_arborescences()
        return new_network

    def pre_calculate_arborescences(self):
        """
        Pre-calculates c edge-disjoint arborescences rooted at each destination.
        For simplicity, this stores c shortest edge-disjoint paths (SEDPs) as
        a dictionary: {destination: {source: [next_hop_c1, next_hop_c2, ...]}}
        """
        connectivity_c = nx.edge_connectivity(self.topology)
        arborescence_store = {}

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
                
            arborescence_store[d] = d_arborescences
            
        self.arborescence_store = arborescence_store # Store the computed structure