# Tools to generate/read topologies
# Author: Leon Okida
# Last modification: 10/26/2025
import networkx as nx

def _set_default_attributes(graph: nx.Graph) -> nx.Graph:
    # Sets default capacity and weight attributes for all edges in the graph
    nx.set_edge_attributes(graph, 1, "capacity")
    nx.set_edge_attributes(graph, 1, "weight")
    return graph

def random_graph(size: int, connectivity: float, max_attempts: int = 100) -> nx.Graph:
    # Generates a connected Erdos-Renyi G(n, p) graph        
    for _ in range(max_attempts):
        graph = nx.erdos_renyi_graph(size, connectivity)
        if nx.is_connected(graph):
            return _set_default_attributes(graph)
    raise ValueError("Failed to generate a connected Erdos-Renyi graph within the maximum attempts.")

def small_world_graph(size: int) -> nx.Graph:
    # Generates a connected Watts-Strogatz small-world graph
    # k=4 (average degree of 4), p=0.4 (rewiring probability)
    graph = nx.connected_watts_strogatz_graph(size, 4, 0.4)
    return _set_default_attributes(graph)

def preferential_attachment_graph(size: int) -> nx.Graph:
    # Generates a Barabasi-Albert graph (preferential attachment)
    # m=3 (number of edges to attach from a new node to existing nodes)
    graph = nx.barabasi_albert_graph(size, 3)
    return _set_default_attributes(graph)

def read_graph(filename: str) -> nx.Graph:
    # Reads a graph from a file
    global_graph = nx.read_edgelist(filename, nodetype=str) # Assume node names are strings
    return _set_default_attributes(global_graph)
