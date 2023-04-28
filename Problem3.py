from mpi4py import MPI
from Graph import Graph
import random
import time
import sys
import datetime

comm = MPI.Comm.Get_parent()  # Listen for parent
rank = comm.Get_rank()
size = comm.Get_size()

self = Graph(None, None)
self = comm.bcast(self, root=0)

self = self.nodes[rank]

comm = MPI.COMM_WORLD  # Interact only with child procs now

neighbors = []
round = 0
clock = rank
expected_responses = 0
payload = {}

while round < size:

    while expected_responses != 0:
        request = comm.irecv()
        data = request.wait()

        if data["round"] == round - 1:
            payload["message"] = "ack"
            payload["round"] = round
            payload["sender"] = rank
            payload["clock"] = clock
            expected_responses -= 1
            clock += 1
            comm.isend(payload, dest=data["sender"])
        else:
            expected_responses -= 1


    payload["message"] = "Payload from {} in round {}".format(rank, round)
    payload["round"] = round
    payload["sender"] = rank
    payload["clock"] = clock
    for node in self.neighbors:
        payload["receiver"] = node
        comm.isend(payload, dest=node, tag=rank)

    expected_responses = (size-1)*2

    round += 1
    print("{}, {}".format(round, datetime.datetime.now()))



