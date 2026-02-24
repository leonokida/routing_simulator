# Simulates routing between two routers in a network using Arborescences
# Author: Leon Okida
# Last modification: 02/23/2026

from routing_sim.simulation_engine.interface import SimulationEngine
from routing_sim.network import Network
from routing_sim.router import Router
from routing_sim.packet import Packet
from routing_sim.metrics import RoutingMetrics
from routing_sim.routing_algorithms.interface import RoutingAlgorithm

class ArborescenceSimulationEngine(SimulationEngine):
    def __init__(self, network: Network, debug_print: bool = False):
        super().__init__()
        self.network = network
        self.metrics = RoutingMetrics(debug_print)
        
    def _find_route_recursive(self, packet: Packet, source_router_name: str | int, algorithm: RoutingAlgorithm):
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
        
        # Loop implements FRR, tries routing along the arborescence or switches in case of failure
        next_hop_list = source_router.get_next_hop_candidates(
            packet=packet,
            global_topology=self.network.topology,
            routing_algorithm=algorithm
        )
        index = algorithm.get_arborescence_index()
        for next_hop in next_hop_list[index:]:
            # Failure found, switches arborescence
            if ((source_router_name, next_hop) in self.failed_edges):
                self.metrics.log_failure(source_router_name, next_hop)
                algorithm.switch_arborescence()
                continue

            # Next hop is found, the packet is forwarded
            self.metrics.log_forwarding(source_router_name, next_hop)
            success = self._find_route_recursive(packet, next_hop, algorithm)

            # Returns successful routing or tries the next option
            if success:
                return True
        
        return False
        
    def simulate_routing(self, source: str | int, dest: str | int, algorithm: RoutingAlgorithm, experiment_name: str, file_path: str) -> tuple:
        # Initiates the routing simulation
        if source not in self.network.routers or dest not in self.network.routers:
            print(f"Error: Source {source} or destination {dest} not found in network.")
            return

        # Initializes the packet
        packet = Packet(origin_name=source, destination_name=dest)
        
        # Routes the packet from source to dest
        algorithm.reset_arborescence_index()
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

    def clean_edge_failures(self) -> None:
        self.failed_edges.clear()