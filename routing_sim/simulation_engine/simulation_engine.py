# Simulates routing between two routers in a network using FRR
# Author: Leon Okida
# Last modification: 05/02/2026

from routing_sim.network import Network
from routing_sim.router import Router
from routing_sim.packet import Packet
from routing_sim.simulation_engine.metrics import RoutingMetrics
from routing_sim.routing_algorithms.interface import RoutingAlgorithm

class SimulationEngine:
    def __init__(self, network: Network, allow_backtracking: bool = True, debug_print: bool = False):
        super().__init__()
        self.network = network
        self.metrics = RoutingMetrics(debug_print)
        self.failed_edges = set()
        self.allow_backtracking = allow_backtracking
        
    def _find_route_recursive(self, packet: Packet, source_router_name: str | int, algorithm: RoutingAlgorithm):
        # Function that simulates the forwarding function
        source_router: Router = self.network.routers.get(source_router_name)
        if not source_router:
            return False
        
        # Records visit
        packet.record_hop(source_router_name)
        dest = packet.destination
        
        # Loop implements FRR, tries all the available routing options
        while True:
            next_hop = source_router.get_next_hop(
                packet=packet,
                global_topology=self.network.topology,
                routing_algorithm=algorithm
            )

            if next_hop is not None:
                if ((source_router_name, next_hop) in self.failed_edges):
                    self.metrics.log_failure(source_router_name, next_hop)
                    algorithm.handle_failure(source_router_name, dest)
                    continue
            
                self.metrics.log_forwarding(source_router_name, next_hop)
                success = self._find_route_recursive(packet, next_hop, algorithm)
            
                if success:
                    return True
                else:
                    if self.allow_backtracking:
                        algorithm.handle_failure(source_router_name, dest)
                    continue
            else:
                break

        # No next hop available
        if self.allow_backtracking:
            parent_router = packet.path[-2] if len(packet.path) > 1 else ""
            self.metrics.log_backtrack(source_router_name, parent_router)
        return False

    def simulate_routing(self, source: str | int, dest: str | int, algorithm: RoutingAlgorithm, experiment_name: str, file_path: str) -> tuple:
        # Initiates the routing simulation
        if source not in self.network.routers or dest not in self.network.routers:
            print("Error: Source or destination not found in network.")
            return
        
        # Initializes the packet
        packet = Packet(origin_name=source, destination_name=dest)

        # Initializes the routing algorithm
        algorithm.initial_setup(source, dest, self.network.topology)
        
        # Routes the packet from source to dest
        success = self._find_route_recursive(packet, source, algorithm)

        # Computes route metrics
        if success:
            self.metrics.compute_metrics(
                file_path=file_path,
                experiment_name=experiment_name,
                algorithm=algorithm,
                packet=packet,
                global_topology=self.network.topology,
                failed_edges = self.failed_edges
            )
        return success, packet.path

    def add_edge_failure(self, edge: tuple) -> None:
        u, v = edge
        self.failed_edges.add((u, v))
        self.failed_edges.add((v, u))
