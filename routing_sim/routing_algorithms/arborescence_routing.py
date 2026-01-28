# The arborecence-based routing algorithm, using a precomputed arborescence packing
# Author: Leon Okida
# Last modification: 01/27/2026

import networkx as nx
from routing_sim.routing_algorithms.interface import RoutingAlgorithm
import copy

class ArborescenceRouting(RoutingAlgorithm):
    def __init__(self):
        super().__init__("Arborescence Routing")
        self.arborescence_packing = dict()
        self.number_of_arborescences = 0
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

        for i in range(j + 1, c):
            intermediate = f"condition_4_i_{i}"
            aux.add_edge(tail, intermediate, capacity=1)
            aux.add_edge(intermediate, r, capacity=1)

        return nx.algorithms.maximum_flow_value(aux, tail, head, flow_func=nx.algorithms.flow.edmonds_karp) >= c - j + 1

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
            candidate_edges = set(topology_digraph.out_edges(r)) - used_edges

            while len(arbo) < len(topology_digraph):
                # Iterates over candidate edges
                iteratable_candidate_edges = sorted(candidate_edges)
                for u, v in iteratable_candidate_edges:
                    # Removes it from usable edges
                    candidate_edges.remove((u, v))
                    
                    # Continues if it's not a valid candidate e*
                    if v in arbo:
                        continue

                    # Checks if it's possible to add the edge to the arborescence
                    if self._condition_4(r, u, v, c, j, topology_digraph, used_edges):
                        arbo.add_edge(u, v)
                        used_edges.add((u, v))
                        candidate_edges.update(set(topology_digraph.out_edges(v)))
                        break

            if not nx.is_arborescence(arbo):
                raise Exception(f"Failed to create a true #{j} {r}-rooted arborescence")

            arborescences.append(arbo.reverse())
            print(f"Created #{j} {r}-rooted arborescence")
        
        return arborescences

    def compute_arborescence_packing(self, topology: nx.Graph) -> None:
        # Computes the arborescence packing
        connectivity_c = nx.edge_connectivity(topology)
        self.number_of_arborescences = connectivity_c
        print(f"The edge-connectivity of the topology is {connectivity_c}")

        # Iterate over every possible destination d
        for d in topology.nodes:
            d_arborescences = self._compute_rooted_arborescences(d, connectivity_c, topology)
            self.arborescence_packing[d] = d_arborescences

    def switch_arborescence(self) -> None:
        self.arborescence_index = (self.arborescence_index + 1) % self.number_of_arborescences

    def calculate_next_hop(self, source: str | int, dest: str | int, global_topology: nx.Graph, visited_names: set) -> list:      
        # Calculates the next hop based on the arborescences
        if dest not in self.arborescence_packing:
            return None

        # Returns the successor of source in the arborescence corresponding to dest (it's the next hop in the path to dest)
        return self.arborescence_packing[dest][self.arborescence_index].successors(source)
