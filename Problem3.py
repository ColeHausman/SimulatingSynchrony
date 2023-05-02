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


# Simulates one round of synchronous activity, with the argument being the message seint
def synchronizer(argument, comm_round, responses, tracker):
    comm_round = comm_round
    if comm_round != 0:
        expected_responses = responses
    else:
        expected_responses = 0
    payload = {}
    responses = []
    # time.sleep(rank)

    # If there are messages to be received
    while expected_responses != 0:
        # Nonblocking recv
        request = comm.irecv()
        data = request.wait()
        # print(data)
        # sys.stdout.flush()
        # If we get a message, it needs to be from the previous round
        if data["round"] == comm_round - 1:
            expected_responses -= 1
            responses.append([data["message"], data["clock"]])
        else:
            print("This should never print")
            sys.stdout.flush()

    # Send the messages to be received in the next round
    # payload["message"] = "Payload from {} in round {}".format(rank, round)
    payload["message"] = argument
    payload["round"] = comm_round
    payload["sender"] = rank
    payload["clock"] = tracker
    for node in self.neighbors:
        payload["receiver"] = node
        comm.isend(payload, dest=node, tag=rank)

    # As the process sent to all neighbours, it should expect (size-1) messages in the next round
    print("Comm round {} has finished for process {}, at {}".format(comm_round, rank, datetime.datetime.now()))
    # print(responses)
    sys.stdout.flush()
    return responses


def test():
    for i in range(5):
        synchronizer("hello", i, size - 1, 1)


test()
