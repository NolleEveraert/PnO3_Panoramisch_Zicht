from mpi4py import MPI
from picamera import PiCamera

RESOLUTION = (2592, 1944)


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    hostname = MPI.Get_processor_name()
    
    with PiCamera(resolution=RESOLUTION) as camera:
        print('start')
        comm.Barrier()
        camera.capture('test.jpg')
            
        print('stop')
    