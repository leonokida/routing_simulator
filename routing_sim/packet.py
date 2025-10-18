class Packet:
    def __init__(self, origin_name: str | int, destination_name: str | int):
        self.origin = origin_name
        self.destination = destination_name
        self.path = [origin_name]
        self.visited = {origin_name}

    def record_hop(self, router_name: str | int):
        self.path.append(router_name)
        self.visited.add(router_name)

    def __str__(self):
        return f"Packet(From: {self.origin} -> To: {self.destination}, Hops: {len(self.path) - 1})"

    def __repr__(self):
        return (f"Packet(origin={repr(self.origin)}, destination={repr(self.destination)}, "
                f"path={repr(self.path)}, visited={repr(self.visited)})")
