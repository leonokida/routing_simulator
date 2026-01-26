# The class that represents a Router
# Author: Leon Okida
# Last modification: 10/26/2025

from routing_sim.packet import Packet
from routing_sim.routing_algorithms.interface import RoutingAlgorithm 
import networkx as nx

class Router:
    def __init__(self, name): 
        self.name = name

    def get_next_hop(self, packet: Packet, global_topology: nx.Graph, routing_algorithm: RoutingAlgorithm) -> str | int | None:
        # Returns the next hop based on the routing algorithm    
        next_hop = routing_algorithm.calculate_next_hop(
            source=self.name,
            dest=packet.destination,
            global_topology=global_topology,
            visited_names=packet.visited 
        )
        return next_hop
