import networkx as nx
from routing_sim.routing_algorithms.interface import RoutingAlgorithm

class ArborescenceRouting(RoutingAlgorithm):
    def __init__(self):
        """
        Args:
            arborescence_store (dict): The structure calculated by Network.pre_calculate_arborescences().
        """
        super().__init__("ArborescenceRouting")
        self.arborescence_store = None
        self.current_arborescence_index = 0

    def add_arborescence_store(self, arborescence_store: dict) -> None:
        self.arborescence_store = arborescence_store

    def calculate_next_hop(self, source, dest, global_topology: nx.Graph, visited_names: set) -> tuple:        
        if dest not in self.arborescence_store:
            return None, float('-inf')

        potential_next_hops = self.arborescence_store.get(dest, {}).get(source, [])
        
        if not potential_next_hops:
            return None, float('-inf')
        for arbo_index in range(len(potential_next_hops)): # Iterate through arborescences (paths)
            next_hop = potential_next_hops[arbo_index]

            if next_hop not in visited_names:
                
                # Get the edge cost (weight)
                try:
                    edge_cost = global_topology[source][next_hop].get('weight', 1)
                    # We use a simple metric: the cost to get to the next hop.
                    return next_hop, -edge_cost 
                except KeyError:
                    # Edge doesn't exist (shouldn't happen if arborescence store is correct)
                    continue

        # If all potential next-hops lead to visited nodes (cycle), we fail.
        return None, float('-inf')