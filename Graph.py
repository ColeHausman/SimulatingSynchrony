class Graph:
    def __init__(self, nodes, size, root=None, graph_type='Undirected'):
        self.nodes = nodes
        self.type = graph_type
        self.size = size
        self.root = root