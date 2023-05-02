from mpi4py import MPI
from Graph import Graph
import time
comm = MPI.Comm.Get_parent() # Listen for parent
rank = comm.Get_rank()
size = comm.Get_size()
import sys

self = Graph(None, None)
self = comm.bcast(self, root=0)

self = self.nodes[rank]

comm = MPI.COMM_WORLD # Interact only with child procs now

rounds = 50
buffer = [[] for i in range(rounds)]


def SynchP(message, round):
    clock = 0
    payload = {}

    #payload["message"] = "Payload from {} in round {}".format(rank, round)
    #if rank == 0:
        #time.sleep(1)
       # print("Sending in round {}".format(round))
        #sys.stdout.flush()
    payload["message"] = message[rank]
    payload["round"] = round
    payload["sender"] = rank
    payload["clock"] = clock
    for node in self.neighbors:
        #print("{} Sending in round {}".format(rank, round))
        #sys.stdout.flush()
        payload["receiver"] = node
        comm.isend(payload, dest=node, tag=rank)
    return len(self.neighbors)
    

def Asynch_recv(num, round):
    track = num

    while track != 0:
        request = comm.irecv()
        data = request.wait()
            #Put the data received in the index of the round in which it was sent
                #TO INDICATE THAT THERE IS DATA TO RECV
        buffer[data["round"]].append([data["message"], data["sender"], data["round"]])
        #Uncomment these three lines to show when messages are received
        #if rank == 1:
            #print(data["round"])
            #sys.stdout.flush()
        track -= 1
    return buffer[round-1]
   
def test_asynch(message):
    i = 0
    while i < rounds:
        num = SynchP([message] * size, i)

        #Uncomment these lines to force the messages to arrive out of order
       # if rank != 2:
           # num = SynchP(i,[message] * size)
     #   if rank == 2 and i < 25: 
       #     num = SynchP(i,[message] * size)
           # num = SynchP(rounds - i-1,[message] * size)

        output = Asynch_recv(num, i)
        if rank == 0:
            print(output)
            sys.stdout.flush()
        i += 1

   # if rank == 0:
        #for j in range(len(buffer)):
           # print(buffer[j])

test_asynch("Hello")