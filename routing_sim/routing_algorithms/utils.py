# Functions to compute Shortest Path and Max Flow values
# Author: Leon Okida
# Last modification: 10/19/2025

import networkx as nx

def get_shortest_path_length(source: str | int, dest: str | int, graph: nx.Graph):
        # Calculates the shortest path length between source and dest using Dijkstra's
        if source == dest:
            return 0
        try:
            return nx.shortest_path_length(graph, source, dest, weight="weight")
        except nx.NetworkXNoPath:
            return float('inf')
        
def get_max_flow_value(source: str | int, dest: str | int, graph: nx.Graph):
        # Calculates the maximum flow value between source and dest
        if source == dest:
            return float('inf')
        try:
            return nx.maximum_flow_value(graph, source, dest, capacity="capacity")
        except:
            return 0