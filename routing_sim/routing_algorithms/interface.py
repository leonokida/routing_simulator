from abc import ABC, abstractmethod
import networkx as nx

class RoutingAlgorithm(ABC):
    """
    Abstract Base Class (Interface) for all routing algorithms.
    
    A concrete implementation must define a method to calculate the 
    best next hop from a source router to a destination.
    """
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    def calculate_next_hop(self, source: str | int, dest: str | int, global_topology: nx.Graph, visited_names: set) -> tuple:
        ...