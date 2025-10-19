# Simulates routing between two routers in a network
# Author: Leon Okida
# Last modification: 10/19/2025

from routing_sim.network import Network
from routing_sim.router import Router
from routing_sim.packet import Packet
from routing_sim.metrics import RoutingMetrics

class SimulationEngine:
    def __init__(self, network: Network, debug_print: bool = True):
        self.network = network
        self.metrics = RoutingMetrics(debug_print=debug_print)
        
    def _find_route_recursive(self, packet: Packet, source_router_name: str | int):
        # Function that simulates the forwarding function
        source_router: Router = self.network.routers.get(source_router_name)
        if not source_router:
            return False
        
        # Records visit
        packet.record_hop(source_router_name)
        dest = packet.destination

        # 1. Destination Reached
        if source_router_name == dest:
            self.metrics.log_success(packet.path)
            return True
        
        # Loop implements FRR, tries all the available routing options
        while True:
            # Get the best available next hop
            next_hop = source_router.get_next_hop(
                packet=packet,
                global_topology=self.network.topology,
            )

            # If no next hop is available, it backtracks
            if next_hop is None:
                parent_router = packet.path[-2] if len(packet.path) > 1 else ""
                self.metrics.log_backtrack(source_router_name, parent_router)                
                packet.record_backtracking_hop()
                return False

            # Next hop is found, the packet is forwarded
            self.metrics.log_forwarding(source_router_name, next_hop)
            success = self._find_route_recursive(packet, next_hop)

            # Returns successful routing or tries the next option
            if success:
                return True
            else:
                self.metrics.log_failure(source_router_name, next_hop)

    def simulate_routing(self, source: str | int, dest: str | int):
        # Initiates the routing simulation
        if source not in self.network.routers or dest not in self.network.routers:
            print("Error: Source or destination not found in network.")
            return

        # Initializes the packet
        packet = Packet(origin_name=source, destination_name=dest)
        
        # Routes the packet from source to dest
        success = self._find_route_recursive(packet, source)

        # Computes route metrics
        self.metrics.compute_final_metrics(packet, self.network.topology)
        
        return success, packet.path
