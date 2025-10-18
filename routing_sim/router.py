from routing_sim.packet import Packet
from routing_sim.routing_algorithms.interface import RoutingAlgorithm 
import networkx as nx

class Router:
    """
    Represents a network router in a routing simulation, capable of making
    forwarding decisions based on an assigned algorithm.
    """
    def __init__(self, name, algorithm: RoutingAlgorithm): 
        """
        Initializes a new Router instance with a specific routing algorithm.

        Args:
            name (str or int): The unique identifier or name of the router.
            algorithm (RoutingAlgorithm): The concrete routing algorithm instance to use.
        """
        self.name = name
        self.routing_table = {} 
        self.routing_algorithm = algorithm 

    def get_next_hop(self, packet: Packet, global_topology: nx.Graph, faulty_names: set) -> str | int | None:
        """
        Uses the assigned routing algorithm to find the best available next hop 
        for the packet toward its destination.
        
        Args:
            packet (Packet): The packet being forwarded (used for destination and visited state).
            global_topology (nx.Graph): The network topology graph.
            faulty_names (set): A set of routers/nodes currently considered unavailable 
                                (used by the simulation's FRR/backtracking logic).
            
        Returns:
            str or int or None: The name of the next router, or None if no valid route is found.
        """
        
        # 1. The core logic is delegated to the specific routing algorithm
        # We pass the combined visited nodes (from packet) and the temporary faulty nodes (from simulation)
        # to the algorithm to ensure it adheres to all constraints.
        
        # Combine cycle-prevention nodes (visited) and simulation blacklisted nodes (faulty)
        blacklist = packet.visited.union(faulty_names)
        
        # For algorithms that only return one best score (like Dijkstra/MultiCriteria):
        if hasattr(self.routing_algorithm, 'calculate_next_hop'):
            next_hop, score = self.routing_algorithm.calculate_next_hop(
                source=self.name,
                dest=packet.destination,
                global_topology=global_topology,
                visited_names=blacklist 
            )
            return next_hop
            
        # For arborescence routing, we pass the full information, including faults
        elif self.routing_algorithm.name == "ArborescenceRouting":
            next_hop, score = self.routing_algorithm.calculate_next_hop(
                source=self.name,
                dest=packet.destination,
                global_topology=global_topology,
                visited_names=packet.visited,
            )
            return next_hop
             
        # Fallback if the algorithm is not recognized or lacks the method
        return None

    def __str__(self):
        """
        Provides a human-readable string representation of the router.
        """
        return f"Router(Name: {self.name}, Algo: {self.routing_algorithm.name}, Entries: {len(self.routing_table)})"

    def __repr__(self):
        """
        Provides an unambiguous string representation of the router object.
        """
        return f"Router(name={repr(self.name)}, algorithm={repr(self.routing_algorithm.name)})"
