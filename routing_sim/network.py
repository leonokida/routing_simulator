import networkx as nx
from routing_sim.router import Router

class Network:
    def __init__(self):
        self.routers = {}
        self.topology = nx.Graph()

    def add_router(self, router_name):
        if router_name not in self.routers:
            new_router = Router(name=router_name)
            self.routers[router_name] = new_router
            self.topology.add_node(router_name)
            return new_router
        return self.routers[router_name]

    def add_link(self, router_a_name, router_b_name, weight=1):
        # Ensure both routers exist before creating the link
        self.add_router(router_a_name)
        self.add_router(router_b_name)
        
        self.topology.add_edge(router_a_name, router_b_name, weight=weight)
    
    @classmethod
    def from_networkx_graph(cls, graph: nx.Graph):
        new_network = cls() # Create an empty Network instance
        
        # 1. Add all nodes as Router objects
        for router_name in graph.nodes:
            new_network.add_router(router_name)
            
        # 2. Add all edges (links)
        for u, v, data in graph.edges(data=True):
            # Use 'weight' attribute if available, otherwise default to 1
            weight = data.get('weight', 1) 
            new_network.add_link(u, v, weight=weight)
            
        return new_network

    def __str__(self):
        return f"Network(Routers: {len(self.routers)}, Links: {self.topology.number_of_edges()})"
    
    def __repr__(self):
        return (f"Network(routers={list(self.routers.keys())}, "
                f"topology_nodes={self.topology.number_of_nodes()}, "
                f"topology_edges={self.topology.number_of_edges()})")