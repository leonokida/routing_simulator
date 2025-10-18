"""
Functions to generate common network topologies (Erdos-Renyi, Watts-Strogatz, 
Barabasi-Albert) and read graph data from files using NetworkX.
"""
import networkx as nx
import random

# --- Helper Function for Edge Attributes ---
def _set_default_attributes(graph: nx.Graph) -> nx.Graph:
    """Sets default 'capacity' and 'weight' attributes for all edges."""
    nx.set_edge_attributes(graph, 1, "capacity")
    nx.set_edge_attributes(graph, 1, "weight")
    return graph

# --- Topology Generation Functions ---

def random_graph(size: int, connectivity: float, max_attempts: int = 100, seed: int = None) -> nx.Graph:
    """Generates a connected Erdos-Renyi G(n, p) graph."""
    if seed is not None:
        random.seed(seed)
        nx.random.seed(seed)
        
    for _ in range(max_attempts):
        # Nodes are automatically 0 to size-1
        graph = nx.erdos_renyi_graph(size, connectivity)
        if nx.is_connected(graph):
            return _set_default_attributes(graph)
            
    raise ValueError("Failed to generate a connected Erdos-Renyi graph within the maximum attempts.")

def small_world_graph(size: int) -> nx.Graph:
    """Generates a connected Watts-Strogatz small-world graph."""
    # k=4 (average degree of 4), p=0.4 (rewiring probability)
    graph = nx.connected_watts_strogatz_graph(size, 4, 0.4)
    return _set_default_attributes(graph)


def preferential_attachment_graph(size: int) -> nx.Graph:
    """Generates a Barabasi-Albert graph (preferential attachment)."""
    # m=3 (number of edges to attach from a new node to existing nodes)
    graph = nx.barabasi_albert_graph(size, 3)
    return _set_default_attributes(graph)


# --- Specific/Famous Graphs ---

def les_miserables() -> nx.Graph:
    """Returns the Les Miserables character co-occurrence graph."""
    graph = nx.les_miserables_graph()
    return _set_default_attributes(graph)

def frucht() -> nx.Graph:
    """Returns the Frucht graph."""
    graph = nx.frucht_graph()
    return _set_default_attributes(graph)

def dgm() -> nx.Graph:
    """Returns the Dorogovtsev-Goltsev-Mendes graph of generation 5."""
    graph = nx.dorogovtsev_goltsev_mendes_graph(5)
    return _set_default_attributes(graph)

def complete_multipartite() -> nx.Graph:
    """Returns a randomly generated complete multipartite graph with 5 partitions."""
    # Note: Using random integers to define the size of each partition
    partition_sizes = [random.randint(10, 25) for _ in range(5)]
    graph = nx.complete_multipartite_graph(*partition_sizes)
    return _set_default_attributes(graph)

# --- Graph Reading Function ---

def read_graph(filename: str) -> nx.Graph:
    """
    Reads a graph from a file (assuming an edge list format) and sets default attributes.
    
    The graph reading functions in NetworkX handle opening/closing files internally.
    """
    global_graph = nx.read_edgelist(filename, nodetype=str) # Assume node names are strings
    return _set_default_attributes(global_graph)
