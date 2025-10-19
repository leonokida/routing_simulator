# The class that represents a Packet
# Author: Leon Okida
# Last modification: 10/19/2025

class Packet:
    def __init__(self, origin_name: str | int, destination_name: str | int):
        self.origin = origin_name
        self.destination = destination_name
        self.path = []
        self.visited = set({})

    def record_hop(self, router_name: str | int):
        # Adds the router name to the current path and visited routers list
        self.path.append(router_name)
        self.visited.add(router_name)

    def record_backtracking_hop(self):
        # Removes the router from the current path
        self.path.pop()
    