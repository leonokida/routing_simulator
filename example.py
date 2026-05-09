import networkx as nx
from routing_sim.routing_algorithms.max_flow_routing import MaxFlowRouting
from routing_sim.routing_algorithms.dijkstra_routing import DijkstraRouting
from routing_sim.routing_algorithms.arborescence_routing import ArborescenceRouting
from routing_sim.network import Network
from routing_sim.simulation_engine.simulation_engine import SimulationEngine
from routing_sim.topology_generation import read_graph, random_graph, remove_low_connectivity_vertices
import random

def create_example_graph():
    G = random_graph(120, 0.3)
    return G

if __name__ == '__main__':
    # --- Configuration ---
    SOURCE = 0
    DESTINATION = 90
    LAMBDA_VALUE = 0.8
    
    # --- Step 1: Create Topology (Graph) ---
    nx_graph = create_example_graph()
    print("Topology Nodes:", list(nx_graph.nodes))

    # --- Step 2: Define and Select Routing Algorithm ---
    ALGORITHM = ArborescenceRouting()
    print(f"Algorithm Selected: {ALGORITHM.name}")

    # --- Step 3 & 4: Create Network and Assign Algorithm ---
    network = Network.from_networkx_graph(remove_low_connectivity_vertices(nx_graph))

    # --- Step 5 & 6: Instantiate and Run Simulation Engine ---
    engine = SimulationEngine(network, allow_backtracking=False, debug_print=True)
    print("Network Initialization Complete.")
    
    # Run the simulation
    success, packet = engine.simulate_routing(SOURCE, DESTINATION, ALGORITHM, "test without failures", "test.csv")
    route = packet.final_route
    idx = random.randrange(len(route) - 1)
    edge_to_fail = (route[idx], route[idx + 1])
    engine.add_edge_failure(edge_to_fail)
    success, packet = engine.simulate_routing(SOURCE, DESTINATION, ALGORITHM, "test with failures", "test.csv")
    
    if success:
        print("\n--- Final Route Found ---")
        print(f"Start: {SOURCE}, End: {DESTINATION}")
        print(f"Path: {' -> '.join(map(str, packet.final_route))}")
        print(f"All hops: {' -> '.join(map(str, packet.hop_history))}")
    else:
        print("\n--- Simulation Failed ---")
        print("No successful path found between source and destination.")
