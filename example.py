import networkx as nx
from routing_sim.routing_algorithms.max_flow_routing import MaxFlowRouting
from routing_sim.routing_algorithms.dijkstra_routing import DijsktraRouting
from routing_sim.routing_algorithms.arborescence_routing import ArborescenceRouting
from routing_sim.network import Network
from routing_sim.simulation_engine import SimulationEngine

def create_example_graph():
    """Creates a graph designed to force FRR and test the routing criteria."""
    G = nx.Graph()
    # Edges: (Source, Dest, Weight, Capacity)
    G.add_edges_from([
        ('A', 'B', {'weight': 1, 'capacity': 1}),  # Path 1 Start
        ('A', 'C', {'weight': 1, 'capacity': 1}),  # Path 2 Start
        ('B', 'D', {'weight': 1, 'capacity': 1}),  # Path 1 Middle
        ('C', 'E', {'weight': 1, 'capacity': 1}),  # Path 2 Middle
        ('D', 'F', {'weight': 1, 'capacity': 1}),  # Path 1 End
        ('E', 'F', {'weight': 10, 'capacity': 1}), # Path 2 End (High Cost)
        
        # Dead end loop to force FRR/Backtracking
        ('D', 'G', {'weight': 1, 'capacity': 1}), 
        ('G', 'H', {'weight': 1, 'capacity': 1}), 
        ('H', 'D', {'weight': 1, 'capacity': 1}), 
    ])
    return G

if __name__ == '__main__':
    # --- Configuration ---
    SOURCE = 'A'
    DESTINATION = 'F'
    LAMBDA_VALUE = 0.5  # Balanced weights (0.5 MF, -0.5 SP)
    
    # --- Step 1: Create Topology (Graph) ---
    nx_graph = create_example_graph()
    print("Topology Nodes:", list(nx_graph.nodes))

    # --- Step 2: Define and Select Routing Algorithm ---
    # Using the complex MultiCriteria logic (MaxFlow + ShortestPath)
    ALGORITHM = ArborescenceRouting()
    print(f"Algorithm Selected: {ALGORITHM.name} (λ={LAMBDA_VALUE})")

    # --- Step 3 & 4: Create Network and Assign Algorithm ---
    network = Network.from_networkx_graph(nx_graph, ALGORITHM)
    ALGORITHM.add_arborescence_store(network.arborescence_store)
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
