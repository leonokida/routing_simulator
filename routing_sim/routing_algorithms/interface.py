# The interface for classes that implement routing algorithms
# Author: Leon Okida
# Last modification: 05/02/2026

from abc import ABC, abstractmethod
import networkx as nx

class RoutingAlgorithm(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def initial_setup(self, source: str | int, dest: str | int, global_topology: nx.Graph) -> None:
        ...
        
    @abstractmethod
    def calculate_next_hop(self, source: str | int, dest: str | int, global_topology: nx.Graph, visited_names: set) -> str | int:
        ...

    @abstractmethod
    def handle_failure(self, source: str | int, dest: str | int) -> None:
        ...
