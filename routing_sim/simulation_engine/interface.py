# Interface of code that simulates routing between two routers in a network
# Author: Leon Okida
# Last modification: 10/27/2025

from abc import ABC, abstractmethod
from routing_sim.routing_algorithms.interface import RoutingAlgorithm


class SimulationEngine(ABC):
    failed_edges = set()

    @abstractmethod
    def simulate_routing(self, source: str | int, dest: str | int, algorithm: RoutingAlgorithm) -> tuple:
        ...
    
    @abstractmethod
    def add_edge_failure(self, edge: tuple) -> None:
        ...