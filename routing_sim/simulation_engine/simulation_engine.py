# Simulates routing between two routers in a network using FRR
# Author: Leon Okida
# Last modification: 10/20/2026

from routing_sim.network import Network
from routing_sim.router import Router
from routing_sim.packet import Packet
from routing_sim.routing_algorithms.interface import RoutingAlgorithm

class SimulationEngine:
    def __init__(self, network: Network, allow_backtracking: bool = True):
        super().__init__()
        self.network = network
        self.failed_edges = set()
        self.allow_backtracking = allow_backtracking
        
    def _find_route_iterative(
        self, 
        packet: Packet, 
        start_router_name: str | int, 
        algorithm: RoutingAlgorithm
    ):
        current_router_name = start_router_name
        
        while current_router_name != None:
            source_router: Router = self.network.routers.get(current_router_name)
            if not source_router:
                return False
            
            # Registers visit
            packet.record_hop(current_router_name)
            dest = packet.destination

            # Success: Destination reached
            if current_router_name == dest:
                return True
            
            found_next_step = False
            
            # FRR
            while True:
                next_hop = source_router.get_next_hop(
                    packet=packet,
                    global_topology=self.network.topology,
                    routing_algorithm=algorithm
                )

                if next_hop is None:
                    break # Options depleted

                # Checks for fail
                if (current_router_name, next_hop) in self.failed_edges:
                    packet.record_failure(current_router_name, next_hop)
                    algorithm.handle_failure(current_router_name, dest)
                    continue # Tries alternate route
                
                # Forwards to next hop
                current_router_name = next_hop
                found_next_step = True
                break

            if found_next_step:
                continue # Continues as the next hop

            # No more routing options: backtracks
            previous_router = packet.final_route[-2] if len(packet.final_route) > 1 else None
            if self.allow_backtracking and previous_router:
                packet.record_backtrack()
                current_router_name = previous_router
            else:
                return False

        return False

    def simulate_routing(
        self, 
        packet: Packet, 
        algorithm: RoutingAlgorithm
    ) -> list | None:
        # Initiates the routing simulation
        source = packet.origin
        dest = packet.destination
        if source not in self.network.routers or dest not in self.network.routers:
            print("Error: Source or destination not found in network.")
            return None
        
        # Initializes the routing algorithm
        algorithm.initial_setup(source, dest, self.network.topology)
        
        # Routes the packet from source to dest
        success = self._find_route_iterative(packet, source, algorithm)

        if success and packet.final_route and packet.final_route[-1] == dest:
            return packet.final_route
        return None

    def add_edge_failure(self, edge: tuple) -> None:
        u, v = edge
        self.failed_edges.add((u, v))
        self.failed_edges.add((v, u))