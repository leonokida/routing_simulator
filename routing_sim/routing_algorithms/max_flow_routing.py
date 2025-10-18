import networkx as nx
from .interface import RoutingAlgorithm

class MaxFlowRouting(RoutingAlgorithm):
    def __init__(self, lambda_val: float = 0.8):
        super().__init__("MaxFlowRouting")
        self.weight_mf = lambda_val
        self.weight_sp = (1 - lambda_val) * -1

    def _get_shortest_path_length(self, source, dest, graph):
        """Calculates the shortest path length using Dijkstra's algorithm (based on 'weight' attribute)."""
        if source == dest:
            return 0
        try:
            # Default weight='weight' for NetworkX shortest path functions
            return nx.shortest_path_length(graph, source, dest, weight="weight")
        except nx.NetworkXNoPath:
            return float('inf')

    def _get_max_flow_value(self, source, dest, graph):
        """Calculates the maximum flow value (based on 'capacity' attribute)."""
        if source == dest:
            return float('inf')
        try:
            # Assumes the 'capacity' attribute is set on edges
            return nx.maximum_flow_value(graph, source, dest, capacity="capacity")
        except:
            # Handle cases where flow calculation fails (e.g., no path or unusual graph structure)
            return 0

    def calculate_next_hop(self, source, dest, global_topology: nx.Graph, visited_names: set) -> tuple:
        best_score = float('-inf')
        best_next_hop = None
        
        neighbors = [n for n in global_topology.neighbors(source) if n != source and n not in visited_names]
        
        if not neighbors:
            return None, float('-inf')

        # Create a temporary graph without the current source node
        temp_graph = global_topology.copy()
        temp_graph.remove_node(source)

        for neighbor in neighbors:
            # 1. Check for reachability (Shortest Path is a good proxy for connectivity)
            # Use the internal function (assuming you moved them inside or made them accessible)
            sp_score = self._get_shortest_path_length(neighbor, dest, temp_graph)

            if sp_score == float('inf'):
                continue 

            # 2. If reachable, calculate both criteria
            mf_score = self._get_max_flow_value(neighbor, dest, temp_graph)
            
            # Apply the weighted formula: (λ * MF) + (-(1-λ) * SP)
            score = (self.weight_mf * mf_score) + (self.weight_sp * sp_score)
            
            if score > best_score:
                best_score = score
                best_next_hop = neighbor

        return best_next_hop, best_score