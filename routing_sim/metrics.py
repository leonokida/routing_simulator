import networkx as nx
from routing_sim.packet import Packet

class RoutingMetrics:
    def __init__(self, debug_print: bool = True):
        self.logs = []
        self.backtrack_counter = 0
        self.debug_print = debug_print

    def log_forwarding(self, router_name, next_hop, reason="FORWARD"):
        """Logs a standard packet hop."""
        log_entry = f"[Router {router_name}] -> Forwarding to {next_hop}. Reason: {reason}"
        self.logs.append(log_entry)
        if self.debug_print:
            print(log_entry)

    def log_failure(self, router_name, failed_next_hop):
        """Logs a failure detection and attempt to reroute/switch options."""
        log_entry = f"[Router {router_name}] !!! FAILURE/LOOP DETECTED: Next hop {failed_next_hop} is unavailable or visited. Trying next option."
        self.logs.append(log_entry)
        if self.debug_print:
            print(log_entry)

    def log_backtrack(self, router_name, previous_router):
        """Logs a backtrack event."""
        self.backtrack_counter += 1
        log_entry = f"[Router {router_name}] <<< BACKTRACK: All options depleted. Returning to {previous_router}."
        self.logs.append(log_entry)
        if self.debug_print:
            print(log_entry)

    def log_success(self, final_route):
        """Logs the final route success."""
        log_entry = f"ROUTE SUCCESS! Final Path: {final_route}"
        self.logs.append(log_entry)
        if self.debug_print:
            print(log_entry)
    
# --- Metric Computation (Implemented as static method for reusability) ---

    @staticmethod
    def _get_number_of_paths_for_node(graph, source, dest):
        """
        Uses max flow (min-cut) to estimate the number of alternate edge-disjoint 
        paths between source and dest.
        """
        try:
            # Assumes 'capacity' is set to 1 for all edges for path counting
            return nx.maximum_flow_value(graph, source, dest, capacity='capacity')
        except nx.NetworkXNoPath:
            return 0
        except Exception:
             # Handle complex flow errors by returning 0
            return 0


    def compute_final_metrics(self, packet: Packet, global_topology: nx.Graph):
        """
        Computes and prints final metrics for the successful route.
        """
        route = packet.path
        if not route or route[-1] != packet.destination:
            print("\n--- Metrics Skipped: Routing failed or incomplete ---")
            return

        print("\n" + "="*40)
        print("SIMULATION METRICS")
        print("="*40)

        # 1. Length of the route
        route_length = len(route) - 1
        print(f"1. Route Length (Hops): {route_length}")

        # 2. Sum of degrees of the vertices in the route
        total_degree = sum(global_topology.degree(node) for node in route)
        print(f"2. Sum of Vertex Degrees: {total_degree}")

        # 3. Average alternate path neighbors
        dest = route[-1]
        temp_graph = global_topology.copy()

        # Remove edges in the used route (simulating failure of the primary path)
        for i in range(len(route) - 1):
            u = route[i]
            v = route[i+1]
            if temp_graph.has_edge(u, v):
                temp_graph.remove_edge(u, v)

        total_alternate_paths = 0
        nodes_to_check = route[1:-1] # Exclude source and destination

        if nodes_to_check:
            # We check max edge-disjoint paths (flow value with capacity=1)
            for node in nodes_to_check:
                alternate_paths = self._get_number_of_paths_for_node(temp_graph, node, dest)
                total_alternate_paths += alternate_paths
            
            avg_alternate_paths = total_alternate_paths / len(nodes_to_check)
            print(f"3. Avg. Alternate Paths (Max Flow): {avg_alternate_paths:.3f}")
        else:
            print("3. Avg. Alternate Paths: N/A (Route too short)")
        
        print(f"Backtracks Performed: {self.backtrack_counter}")
        print("="*40)