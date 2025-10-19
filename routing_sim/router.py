# The class that represents a Router
# Author: Leon Okida
# Last modification: 10/19/2025

from routing_sim.packet import Packet
from routing_sim.routing_algorithms.interface import RoutingAlgorithm 
import networkx as nx

class Router:
    def __init__(self, name, algorithm: RoutingAlgorithm): 
        self.name = name
        self.routing_table = {} 
        self.routing_algorithm = algorithm 

    def get_next_hop(self, packet: Packet, global_topology: nx.Graph) -> str | int | None:
        # Returns the next hop based on the routing algorithm    
        next_hop, score = self.routing_algorithm.calculate_next_hop(
            source=self.name,
            dest=packet.destination,
            global_topology=global_topology,
            visited_names=packet.visited 
        )
        return next_hop
