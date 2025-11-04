# The arborecence-based routing algorithm, using a precomputed arborescence packing
# Author: Leon Okida
# Last modification: 11/03/2025

import networkx as nx
from routing_sim.routing_algorithms.interface import RoutingAlgorithm
import copy

class ArborescenceRouting(RoutingAlgorithm):
    def __init__(self):
        super().__init__("ArborescenceRouting")
        self.arborescence_packing = dict()
        self.arborescence_index = 0

    def _condition_1(self, r: str | int, c: int, topology: nx.DiGraph) -> bool:
        # Tests condition 1 of Tarjan's Algorithm
        aux = copy.deepcopy(topology)
        source = "condition_1_s"
        aux.add_node(source)

        for i in range(c):
            intermediate = f"condition_1_i_{i}"
            aux.add_edge(source, intermediate, capacity=1)
            aux.add_edge(intermediate, r, capacity=1)

        for node in sorted(topology.nodes()):
            if nx.algorithms.maximum_flow_value(aux, source, node, flow_func=nx.algorithms.flow.edmonds_karp) < c:
                return False
        
        return True
    
    def _condition_4(self, r: str | int, tail: str | int, head: str | int, c: int, j: int, topology: nx.DiGraph, used_edges: set) -> bool:
        # Tests condition 4 of Tarjan's Algorithm
        aux = copy.deepcopy(topology)
        for edge in used_edges:
            aux.remove_edge(*edge)

        for i in range(j, c):
            intermediate = f"condition_4_i_{i}"
            aux.add_edge(tail, intermediate, capacity=1)
            aux.add_edge(intermediate, r, capacity=1)

        return nx.algorithms.maximum_flow_value(aux, tail, head, flow_func=nx.algorithms.flow.edmonds_karp) >= c - j

    def _compute_rooted_arborescences(self, r: str | int, c: int, topology: nx.Graph) -> list[nx.DiGraph]:
        # Uses the Tarjan algorithm to generate c r-rooted arborescences
        
        # Transforms topology into a digraph
        topology_digraph = topology.to_directed()

        used_edges = set()
        arborescences = list()

        # Checks if it's possible to compute c r-rooted arborescences
        if not self._condition_1(r, c, topology_digraph):
            raise Exception(f"Failed condition 1 to create {c} {r}-rooted arborescences")
        
        for j in range(1, c + 1):
            arbo = nx.DiGraph()
            arbo.add_node(r)

            usable_edges = set(topology_digraph.edges()) - used_edges

            while set(arbo.nodes()) != set(topology_digraph.nodes()):
                progress = False

                # Iterates over usable edges
                for u, v in sorted(usable_edges):
                    # Finds candidate e*
                    if u in arbo and v not in arbo:
                        # Removes from usable edges
                        usable_edges.remove((u, v))

                        # Checks if it's possible to add the edge to the arborescence
                        if self._condition_4(r, u, v, c, j, topology_digraph, used_edges):
                            arbo.add_edge(u, v)
                            progress = True
                            break

                if not progress:
                    raise Exception(f"The algorithm stagnated while building the #{j} {r}-rooted arborescence")

            # Updates the used edges set
            used_edges.update(arbo.edges())
            arborescences.append(arbo)
            print(f"Created #{j} {r}-rooted arborescence")
        
        return arborescences

    def compute_arborescence_packing(self, topology: nx.Graph) -> None:
        # Computes the arborescence packing
        connectivity_c = nx.edge_connectivity(topology)

        # Iterate over every possible destination d
        for d in topology.nodes:
            d_arborescences = self._compute_rooted_arborescences(d, connectivity_c, topology)
            self.arborescence_packing[d] = d_arborescences

    def calculate_next_hop(self, source: str | int, dest: str | int, global_topology: nx.Graph, visited_names: set) -> tuple:      
        # Calculates the next hop based on the arborescences
        if dest not in self.arborescence_packing:
            return None, float('-inf')

        # Returns the predecessor of source in the arborescence corresponding to dest (it's the next hop in the path to dest)
        for next_hop in self.arborescence_packing[dest][self.arborescence_index].predecessors(source):
            return next_hop, 1

        return None, float('-inf')