# The interface for classes that implement routing algorithms
# Author: Leon Okida
# Last modification: 10/27/2025

from abc import ABC, abstractmethod
import networkx as nx

class RoutingAlgorithm(ABC):
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    def calculate_next_hop(self, source: str | int, dest: str | int, global_topology: nx.Graph, visited_names: set) -> list:
        ...

    @abstractmethod
    def switch_arborescence(self) -> None:
        ...