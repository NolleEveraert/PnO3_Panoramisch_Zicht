
import numpy
from mpi4py import MPI

print('test')

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
print(rank)

if rank == 0:
    data = {'a':7, 'b':5}
    comm.send(data,dest=1,tag=11)
    print('from rank 0:')
    print(data)
else:
    data = comm.recv(source=0,tag=11)
    print(data)
    