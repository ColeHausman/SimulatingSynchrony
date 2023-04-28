class Vertex:
    def __init__(self, id, neighbors, parent=None, active=True):
        self.id = id
        self.neighbors = neighbors
        self.parent = parent
        self.active = active