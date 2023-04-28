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

responses = []
round = 0
clock = rank
expected_responses = 0


def synchronizer(round, clock, expected_responses, responses):
    accessing = False
    response_string = ""
    payload = {}
    while round < size:
        while expected_responses != 0:
            # Get messages
            request = comm.irecv()
            data = request.wait()
            # If the message is from the previous round
            if data["round"] == round - 1:
                # Reduce the number of expected messages
                expected_responses -= 1

                payload["message"] = "ack"
                payload["round"] = round
                payload["sender"] = rank
                payload["clock"] = clock
                clock += 1
                # Send the ack message
                comm.isend(payload, dest=data["sender"])
                # If it is an odd round, we are getting a REQUEST message and need to decide how to respond
                if round % 2 == 1:
                    print("clock: {}, recv clock: {}".format(clock, data["clock"]))
                    sys.stdout.flush()
                    if clock < data["clock"]:
                        response_string = "allow"
                    elif clock == data["clock"] and rank < data["sender"]:
                        response_string = "allow"
                    else:
                        response_string = "denial"
                # Else it IS a RESPONSE string and tells us what we can or cannot do
                else:
                    responses.append(data["message"])
            else:
                expected_responses -= 1

        if round % 2 == 0:  # even round
            if not accessing:
                payload["message"] = "request"
            else:
                payload["message"] = "accessing"
            payload["round"] = round
            payload["sender"] = rank
            payload["clock"] = clock
            for node in self.neighbors:
                clock += 1
                print("{} clock is {}".format(rank, clock))
                sys.stdout.flush()
                payload["receiver"] = node
                comm.isend(payload, dest=node, tag=rank)
            # If it is an even round, we got responses to whether or not we can access
            if round != 0:
                #print("proc {} has {}".format(rank, responses))
                if "denial" or "accessing" not in responses and responses != []:
                    print("{} is accessing the resource".format(rank))
                    sys.stdout.flush()
                    accessing = True
        else:
            # ODD ROUND WE ARE RESPONDING TO A REQUEST
            payload["message"] = response_string
            payload["round"] = round
            payload["sender"] = rank
            payload["clock"] = clock
            for node in self.neighbors:
                clock += 1
                print("{} clock is {}".format(rank, clock))
                payload["receiver"] = node
                comm.isend(payload, dest=node, tag=rank)



            else:
                responses = []

        expected_responses = (size - 1) * 2
        round += 1
        #print("{}, {}".format(round, datetime.datetime.now()))


synchronizer(0, rank, 0, responses)