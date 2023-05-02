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

rounds = 50


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
    # print("Comm round {} has finished for process {}, at {}".format(comm_round, rank, datetime.datetime.now()))
    # print(responses)
    # sys.stdout.flush()
    return responses


def test_mutex():
    response = ["request"] * (size - 1)
    k = False
    accesses = 1
    tracker = rank
    num_rounds = random.randint(1, 3)
    for i in range(rounds):
        # Sends the requests to the other processes
        # print(response)
        # sys.stdout.flush()
        value = synchronizer(response[(rank - 1)], i, size - 1, tracker * accesses)
        # value = combo(response[(rank-1)], i, size-1, tracker*accesses)
        # print("Value = {} for process {} during round {}".format(value, rank, i))
        # Primes the repsonse array for the response to the request

        if value != []:
            # There is currently a process in crit
            if k == True:
                response = ["Currently Accessing"] * (size - 1)
            # Decide which process will enter
            if any("request" in sublist for sublist in value):
                response = ["accessing"] * (size - 1)
                # Make the decision as to who gets access to the resource
                for j in range(size - 1):
                    if value != []:
                        if tracker * accesses > value[j][1]:
                            response[rank - 1] = "denial"
            else:
                response = ["denial"] * (size - 1)

        if "denial" not in response and value != [] and k == False:
            tracker += size
            accesses += 1
            print(
                "Rank {} is accessing the resource during loop {}. This process has accessed the shared resource {} times.".format(
                    rank, i, accesses))
            sys.stdout.flush()
            response = ["Currently Accessing"] * (size - 1)
            k = True
        elif k == True:
            num_rounds -= 1
            if num_rounds == 0:
                print("Rank {} is leaving the resource during loop {}.".format(rank, i))
                sys.stdout.flush()
                response = ["free"] * (size - 1)
                k = False
                num_rounds = random.randint(1, 3)
        for j in range(size - 1):
            if value != []:
                if "free" in value[j]:
                    response = ["request"] * (size - 1)


def SynchP(message, round):
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


def Asynch_recv(num, round):
    track = num
    responses = [[] for i in range(rounds)]

    while track != 0:
        request = comm.irecv()
        data = request.wait()
        # Put the data received in the index of the round in which it was sent
        # TO INDICATE THAT THERE IS DATA TO RECV

        responses[data["round"]].append([data["message"], data["sender"]])
        track -= 1
    # print("Printing {}\n {}".format(rank, buffer))
    return responses


def combo(argument, round, responses, tracker):
    val = SynchP(argument, round)
    output = Asynch_recv(val, round)
    print(output)
    sys.stdout.flush()
    return output


test_mutex()
