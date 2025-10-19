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
            
        return new_network
    