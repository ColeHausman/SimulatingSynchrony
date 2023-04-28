import time
import sys

from tqdm import tqdm
from Vertex import Vertex
from Graph import Graph


def is_cyclic_util(Graph, v, visited, parent):
    visited[v] = True

    for neighbor in Graph.nodes[v].neighbors:
        try:
            if not visited[neighbor]:
                if is_cyclic_util(Graph, neighbor, visited, v):
                    return True

            elif neighbor != parent:
                return True
        except IndexError:
            print("{}Error neighbor {} not found in the graph".
                  format('\033[91m', neighbor))
            exit(-1)
    return False


def check_tree_topology(Graph):
    visited = [False] * Graph.size

    if is_cyclic_util(Graph, Graph.root, visited, -1):
        return False

    for i in range(Graph.size):
        if not visited[i]:
            return False

    return True


def check_ring_topology(nodes):
    num_edges = 0
    edges = {}

    if len(nodes) <= 2:
        return False

    for key, node in nodes.items():
        if len(node.neighbors) != 2:
            return False
        for neighbor in node.neighbors:
            first = min(node.id, neighbor)
            second = neighbor if first == node.id else node.id
            if not (first, second) in edges:
                edges[(first, second)] = 1
                num_edges += 1

    if num_edges != len(nodes):
        return False

    return True


def parse_nodes(filename):
    print("parsing {} ...".format(filename))
    nodes = {}
    size = 0
    root = None
    with open(filename, 'r') as f:
        for line in tqdm(f.readlines()):
            try:
                vertex_id = int(line.partition(":")[0])
                neighbors = list(map(int, line.partition(":")[2].strip().split(",")))
                nodes[vertex_id] = Vertex(vertex_id, neighbors)

                if vertex_id in neighbors:
                    if root is not None:
                        print("{}Error: only 1 root allowed\n Root already declared as {}".
                              format('\033[91m', root))
                        exit(-1)
                    root = nodes[vertex_id].id
                    nodes[vertex_id].parent = root
                    neighbors.remove(vertex_id)

                size += 1
                time.sleep(0.001)
            except:
                print("{}Expected format i[int]: np[int], n1[int], n2[int],...\n instead got: {}".
                      format('\033[91m', line))
                exit(-1)
    retval = Graph(nodes, size, root)
    print("checking topology...")
    if check_ring_topology(nodes):
        retval.type = 'Ring'

    if retval.root is not None:
        if check_tree_topology(retval):
            retval.type = 'Rooted Tree'

    if retval.type != 'Ring':
        for key, vertex in retval.nodes.items():
            if vertex.id != retval.root:
                vertex.parent = vertex.neighbors[0]

    print("{}{} graph created successfully{}".
          format('\033[96m', retval.type, '\033[0m'))
    sys.stdout.flush()
    return retval