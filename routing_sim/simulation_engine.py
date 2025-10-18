from routing_sim.network import Network
from routing_sim.router import Packet
from routing_sim.metrics import RoutingMetrics

class SimulationEngine:
    """Simulates packet forwarding across the network, including FRR and Backtracking."""
    def __init__(self, network: Network, debug_print: bool = True):
        self.network = network
        self.metrics = RoutingMetrics(debug_print=debug_print)
        
    def _find_route_recursive(self, packet: Packet, source_router_name):
        """Core recursive function with FRR and Backtracking."""
        source_router = self.network.routers.get(source_router_name)
        if not source_router:
            return False 
        
        dest = packet.destination

        # 1. Destination Reached
        if source_router_name == dest:
            self.metrics.log_success(packet.path)
            return True

        # Set for nodes that failed downstream during the current router's attempt (FRR blacklist)
        temporary_faulty_set = set() 
        
        # Loop implements 'trying the next options until depleted' (FRR)
        while True:
            # Get the best available next hop, avoiding visited and temporarily faulty nodes
            next_hop = source_router.get_next_hop(
                packet=packet,
                global_topology=self.network.topology,
                faulty_names=temporary_faulty_set
            )

            # 2. Check Next Hop Result
            if next_hop is None:
                # --- Backtracking (Options Depleted) ---
                parent_router = packet.path[-2] if len(packet.path) > 1 else "START"
                self.metrics.log_backtrack(source_router_name, parent_router)
                
                # Remove current node from path (backtrack)
                packet.path.pop() 
                # packet.visited remains untouched here to prevent cycles back to this branch's roots
                return False 

            # 3. Successful Forwarding (Next Hop Found)
            
            self.metrics.log_forwarding(source_router_name, next_hop)
            
            # Record the hop before recursion
            packet.path.append(next_hop)
            packet.visited.add(next_hop)

            # Recursion (Simulate forwarding the packet)
            success = self._find_route_recursive(packet, next_hop)

            if success:
                return True
            else:
                # --- FRR/Failure Detection on Return (Downstream Failure) ---
                
                self.metrics.log_failure(source_router_name, next_hop)
                
                # 1. Clean up the failed branch's state
                if next_hop in packet.path:
                    packet.path.remove(next_hop)
                if next_hop in packet.visited:
                    packet.visited.remove(next_hop) 
                
                # 2. Mark the failed next_hop as temporarily faulty/unusable for the *current* router
                temporary_faulty_set.add(next_hop) 
                
                # 3. Loop continues (FRR): Algorithm re-calculates the next best hop.


    def simulate_routing(self, source, dest):
        """Initiates the routing simulation."""
        if source not in self.network.routers or dest not in self.network.routers:
            print("Error: Source or destination not found in network.")
            return

        # Initialize the packet
        packet = Packet(origin_name=source, destination_name=dest)
        
        # Start the recursive search
        success = self._find_route_recursive(packet, source)

        # Compute and display final metrics
        self.metrics.compute_final_metrics(packet, self.network.topology)
        
        return success, packet.path