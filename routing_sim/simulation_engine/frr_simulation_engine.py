# Simulates routing between two routers in a network using FRR
# Author: Leon Okida
# Last modification: 01/27/2026

from routing_sim.simulation_engine.interface import SimulationEngine
from routing_sim.network import Network
from routing_sim.router import Router
from routing_sim.packet import Packet
from routing_sim.metrics import RoutingMetrics
from routing_sim.routing_algorithms.interface import RoutingAlgorithm

class FRRSimulationEngine(SimulationEngine):
    def __init__(self, network: Network, debug_print: bool = True):
        super().__init__()
        self.network = network
        self.metrics = RoutingMetrics(debug_print=debug_print)
        
    def _find_route_recursive(self, packet: Packet, source_router_name: str | int, algorithm: RoutingAlgorithm):
        # Function that simulates the forwarding function
        source_router: Router = self.network.routers.get(source_router_name)
        if not source_router:
            return False
        
        # Records visit
        packet.record_hop(source_router_name)
        dest = packet.destination

        # Ends routing if it reached destination
        if source_router_name == dest:
            self.metrics.log_success(packet.path)
            return True
        
        # Loop implements FRR, tries all the available routing options
        candidate_index = 0
        while True:
            # Get the best available next hop
            next_hop_candidates = source_router.get_next_hop(
                packet=packet,
                global_topology=self.network.topology,
                routing_algorithm=algorithm
            )

            # If no next hop is available, it backtracks
            if (candidate_index >= len(next_hop_candidates)) or (next_hop_candidates is None):
                parent_router = packet.path[-2] if len(packet.path) > 1 else ""
                self.metrics.log_backtrack(source_router_name, parent_router)                
                packet.record_backtracking_hop()
                return False
        
            next_hop = next_hop_candidates[candidate_index]
            
            # Failure detected on the link to the next hop
            if ((source_router_name, next_hop) in self.failed_edges):
                self.metrics.log_failure(source_router_name, next_hop)
                next_hop_candidates += 1
                continue

            # Next hop is found, the packet is forwarded
            self.metrics.log_forwarding(source_router_name, next_hop)
            success = self._find_route_recursive(packet, next_hop, algorithm)

            # Returns successful routing or tries the next option
            if success:
                return True
            else:
                self.metrics.log_failure(source_router_name, next_hop)
                next_hop_candidates += 1

    def simulate_routing(self, source: str | int, dest: str | int, algorithm: RoutingAlgorithm, experiment_name: str, file_path: str) -> tuple:
        # Initiates the routing simulation
        if source not in self.network.routers or dest not in self.network.routers:
            print("Error: Source or destination not found in network.")
            return

        # Initializes the packet
        packet = Packet(origin_name=source, destination_name=dest)
        
        # Routes the packet from source to dest
        success = self._find_route_recursive(packet, source, algorithm)

        # Computes route metrics
        self.metrics.compute_final_metrics(packet, self.network.topology)
        self.metrics.save_metrics_to_csv(
            file_path=file_path,
            experiment_name=experiment_name,
            algorithm=algorithm,
            packet=packet,
            global_topology=self.network.topology
        )
        
        return success, packet.path

    def add_edge_failure(self, edge: tuple) -> None:
        u, v = edge
        self.failed_edges.add((u, v))
        self.failed_edges.add((v, u))