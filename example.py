# In your main simulation script:
import networkx as nx
from routing_sim.network import Network
from routing_sim import topology_generation

# 1. Generate a NetworkX graph using the new module
nx_graph = topology_generation.small_world_graph(size=50)

# 2. Convert the NetworkX graph into your Network object
sim_network = Network.from_networkx_graph(nx_graph)

print(sim_network)
# Network(Routers: 50, Links: X)