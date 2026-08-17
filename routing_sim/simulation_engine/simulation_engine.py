# Simulates routing between two routers in a network using FRR
# Author: Leon Okida
# Last modification: 08/17/2026

from routing_sim.network import Network
from routing_sim.router import Router
from routing_sim.packet import Packet
from routing_sim.simulation_engine.metrics import Metrics
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
        algorithm: RoutingAlgorithm,
        metrics: Metrics
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
                metrics.log_success(packet.final_route)
                metrics.log_hop_history(packet.hop_history)
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
                    metrics.log_failure(current_router_name, next_hop)
                    algorithm.handle_failure(current_router_name, dest)
                    continue # Tries alternate route
                
                # Forwards to next hop
                metrics.log_forwarding(current_router_name, next_hop)
                current_router_name = next_hop
                found_next_step = True
                break

            if found_next_step:
                continue # Continues as the next hop

            # No more routing options: backtracks
            previous_router = packet.final_route[-2] if len(packet.final_route) > 1 else None
            if self.allow_backtracking and previous_router:
                metrics.log_backtrack(current_router_name, previous_router)
                packet.record_backtrack()
                current_router_name = previous_router
            else:
                return False

        return False

    def simulate_routing(
        self, 
        source: str | int, 
        dest: str | int, 
        algorithm: RoutingAlgorithm,
        metrics: Metrics,
        experiment_name: str, 
        file_path: str
    ) -> tuple:
        # Initiates the routing simulation
        if source not in self.network.routers or dest not in self.network.routers:
            print("Error: Source or destination not found in network.")
            return
        
        # Initializes the packet
        packet = Packet(origin_name=source, destination_name=dest)

        # Initializes the routing algorithm
        algorithm.initial_setup(source, dest, self.network.topology)
        
        # Routes the packet from source to dest
        success = self._find_route_iterative(packet, source, algorithm, metrics)

        # Computes route metrics
        if success and file_path:
            metrics.compute_metrics(
                file_path=file_path,
                experiment_name=experiment_name,
                algorithm=algorithm,
                packet=packet,
                global_topology=self.network.topology,
                failed_edges = self.failed_edges
            )

        return success, packet

    def add_edge_failure(self, edge: tuple) -> None:
        u, v = edge
        self.failed_edges.add((u, v))
        self.failed_edges.add((v, u))