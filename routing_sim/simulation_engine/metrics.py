# Abstract methods for logging and metrics
# Author: Leon Okida
# Last modification: 08/17/2026

from abc import ABC, abstractmethod
import networkx as nx
from routing_sim.packet import Packet
from routing_sim.routing_algorithms.interface import RoutingAlgorithm

class Metrics(ABC):
    @abstractmethod
    def log_forwarding(self, router_name: str | int, next_hop: str | int):
        ...

    @abstractmethod
    def log_failure(self, router_name: str | int, failed_next_hop: str | int):
        ...

    @abstractmethod
    def log_backtrack(self, router_name: str | int, previous_router: str | int):
        ...

    def log_success(self, final_route: list):
        ...

    def log_hop_history(self, hop_history: list):
        ...
        
    def compute_metrics(
        self, 
        file_path: str, 
        experiment_name: str, 
        algorithm: RoutingAlgorithm, 
        packet: Packet, 
        global_topology: nx.Graph, 
        failed_edges: set
    ):
        ...