class Router:
    def __init__(self, name: str | int):
        self.name = name
        self.routing_table = dict()

    def __str__(self):
        return f"Router(Name: {self.name}, Entries: {len(self.routing_table)})"

    def __repr__(self):
        return f"Router(name={repr(self.name)}, routing_table={repr(self.routing_table)})"
    