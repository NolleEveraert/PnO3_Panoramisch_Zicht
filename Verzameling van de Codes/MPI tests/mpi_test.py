print('test voor import')
import numpy
import mpi4py
mpi4py.rc.initialize = False
mpi4py.rc.finalize = False
from mpi4py import MPI

print('test')

MPI.Init()
print('test na MPI initialisatie')

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
hostname = MPI.Get_processor_name()
print(hostname)
print(size)
print(rank)

if rank == 0:
    data = {'a':7, 'b':5}
    comm.send(data,dest=1,tag=11)
    print('from rank 0:')
    print(data)
else:
    data = comm.recv(source=0,tag=11)
    print(data)
    
MPI.Finalize()
print('test na Finalize')
    