import networkx as nx
from routing_sim.routing_algorithms.interface import RoutingAlgorithm

class DijsktraRouing(RoutingAlgorithm):
    def __init__(self):
        super().__init__("ShortestPath")

    def _get_shortest_path_length(self, source, dest, graph):
        """Calculates the shortest path length using Dijkstra's algorithm (based on 'weight' attribute)."""
        if source == dest:
            return 0
        try:
            # Default weight='weight' for NetworkX shortest path functions
            return nx.shortest_path_length(graph, source, dest, weight="weight")
        except nx.NetworkXNoPath:
            return float('inf')

    def calculate_next_hop(self, source: str | int, dest: str | int, global_topology: nx.Graph, visited_names: set) -> tuple:
        best_score = float('inf')
        best_next_hop = None
        
        # Consider only unvisited neighbors that are not the source itself
        neighbors = [n for n in global_topology.neighbors(source) if n != source and n not in visited_names]
        
        if not neighbors:
            return None, float('-inf')
        temp_graph = global_topology.copy()
        temp_graph.remove_node(source)

        for neighbor in neighbors:
            # Score is the distance from the neighbor to the destination
            score = self._get_shortest_path_length(neighbor, dest, temp_graph)
            
            if score < best_score:
                best_score = score
                best_next_hop = neighbor
        
        if best_next_hop is not None and best_score != float('inf'):
            edge_cost = global_topology[source][best_next_hop].get('weight', 1)
            final_score = edge_cost + best_score
            return best_next_hop, final_score
        
        return None, float('-inf')
