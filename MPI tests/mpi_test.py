from picamera import PiCamera
from time import sleep
import numpy
from mpi4py import MPI

WIDTH = 1600
HEIGHT = 800

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    data = {'a':7, 'b':5}
    comm.send(data,dest=1,tag=11)
    print('from rank 0:')
    print(data)
else:
    data = comm.recv(source=0,tag=11)
    print(data)
    

with PiCamera() as camera:
    camera.start_preview()
    sleep(5)
    camera.stop_preview()