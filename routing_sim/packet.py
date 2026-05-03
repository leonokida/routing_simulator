# The class that represents a Packet
# Author: Leon Okida
# Last modification: 05/03/2026

class Packet:
    def __init__(self, origin_name: str | int, destination_name: str | int):
        self.origin = origin_name
        self.destination = destination_name
        self.final_route = []
        self.hop_history = []
        self.visited = set({})

    def record_hop(self, router_name: str | int):
        # Adds the router name to the current route and visited routers list
        self.final_route.append(router_name)
        self.hop_history.append(router_name)
        self.visited.add(router_name)

    def record_backtrack(self):
        self.final_route = self.final_route[:-2]
