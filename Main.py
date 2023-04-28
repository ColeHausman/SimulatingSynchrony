from mpi4py import MPI
import sys
import os
from GraphParser import parse_nodes


comm = MPI.COMM_WORLD
rank = comm.Get_rank()

graph_file = sys.argv[2] #The first argument given by the user is the file to make a graph
file_to_run = sys.argv[1]
if not os.path.isfile(graph_file): #If the file provided does not exist
    print("Graph txt file not found, please make sure file existed")
graph = parse_nodes(graph_file) #Create a graph from the provided file



comm = MPI.COMM_SELF.Spawn(sys.executable,
                           args=[file_to_run],
                           maxprocs=5) #Spawn the processes

comm.bcast(graph, root=MPI.ROOT) #Broadcast the root to the processes

comm.Disconnect()
