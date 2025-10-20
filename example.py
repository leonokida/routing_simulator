import networkx as nx
from routing_sim.routing_algorithms.max_flow_routing import MaxFlowRouting
from routing_sim.routing_algorithms.dijkstra_routing import DijsktraRouting
from routing_sim.routing_algorithms.arborescence_routing import ArborescenceRouting
from routing_sim.network import Network
from routing_sim.simulation_engine import SimulationEngine
from routing_sim.topology_generation import read_graph

def create_example_graph():
    """Creates a graph designed to force FRR and test the routing criteria."""
    G = read_graph("topologies/rnp_equal.txt")
    return G

if __name__ == '__main__':
    # --- Configuration ---
    SOURCE = 'curitiba'
    DESTINATION = 'vitoria'
    LAMBDA_VALUE = 0.8
    
    # --- Step 1: Create Topology (Graph) ---
    nx_graph = create_example_graph()
    print("Topology Nodes:", list(nx_graph.nodes))

    # --- Step 2: Define and Select Routing Algorithm ---
    ALGORITHM = ArborescenceRouting()

    # Uncomment line below to use Arborescence Routing
    ALGORITHM.compute_arborescence_packing(nx_graph)

    print(f"Algorithm Selected: {ALGORITHM.name}")
    if ALGORITHM.name == "MaxFlowRouting":
        print("Lambda:", LAMBDA_VALUE)

    # --- Step 3 & 4: Create Network and Assign Algorithm ---
    network = Network.from_networkx_graph(nx_graph, ALGORITHM)
    network.from_networkx_graph(nx_graph, ALGORITHM)
    print("Network Initialization Complete.")

    # --- Step 5 & 6: Instantiate and Run Simulation Engine ---
    engine = SimulationEngine(network, debug_print=True)
    
    # Run the simulation (Start: A, Destination: F)
    success, route = engine.simulate_routing(SOURCE, DESTINATION)
    
    if success:
        print("\n--- Final Route Found ---")
        print(f"Start: {SOURCE}, End: {DESTINATION}")
        print(f"Path: {' -> '.join(map(str, route))}")
    else:
        print("\n--- Simulation Failed ---")
        print("No successful path found between source and destination.")
