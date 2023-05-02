from mpi4py import MPI
from Graph import Graph
import random
import time
import sys

comm = MPI.Comm.Get_parent()  # Listen for parent
rank = comm.Get_rank()
size = comm.Get_size()

self = Graph(None, None)
self = comm.bcast(self, root=0)

self = self.nodes[rank]

comm = MPI.COMM_WORLD  # Interact only with child procs now

buffer = [[] for i in range(10)]


def SynchP(round, message):
    clock = 0
    payload = {}
    # payload["message"] = "Payload from {} in round {}".format(rank, round)
    # if rank == 0:
    # print("Sending in round {}".format(round))
    # sys.stdout.flush()
    payload["message"] = message[rank]
    payload["round"] = round
    payload["sender"] = rank
    payload["clock"] = clock
    for node in self.neighbors:
        # print("{} Sending in round {}".format(rank, round))
        # sys.stdout.flush()
        payload["receiver"] = node
        comm.isend(payload, dest=node, tag=rank)
    return len(self.neighbors)


def Asynch_recv(num):
    track = num
    while track != 0:
        request = comm.irecv()
        data = request.wait()
        # Put the data received in the index of the round in which it was sent
        # TO INDICATE THAT THERE IS DATA TO RECV

        buffer[data["round"]].append([data["message"], data["sender"], data["round"]])
        track -= 1
    # print("Printing {}\n {}".format(rank, buffer))


def Example():
    i = 0
    while i < 10:
        num = SynchP(i, ["Message"] * size)
        Asynch_recv(num)
        i += 1

    if rank == 0:
        print(buffer)


Example()