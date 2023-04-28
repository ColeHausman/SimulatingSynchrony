from mpi4py import MPI
from Graph import Graph
import random
import time

comm = MPI.Comm.Get_parent() # Listen for parent
rank = comm.Get_rank()
size = comm.Get_size()

self = Graph(None, None)
self = comm.bcast(self, root=0)

self = self.nodes[rank]

comm = MPI.COMM_WORLD # Interact only with child procs now

clock = 0
received = [[None] for i in range(size)]
round = 0
payload = {}
while round < size:
    payload["message"] = "Payload from {} in round {}".format(rank, round)
    payload["round"] = round
    payload["sender"] = rank
    payload["clock"] = clock
    for node in self.neighbors:
        payload["receiver"] = node
        comm.isend(payload, dest=node, tag=rank)

    request = comm.irecv()
    data = request.wait()
    received[data["round"]].append(data["message"])
    round += 1

print("Printing {}\n {}".format(rank, received))