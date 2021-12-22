from mpi4py import MPI
from picamera import PiCamera
from time import sleep

RESOLUTION = (2592, 1944)


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    hostname = MPI.Get_processor_name()
    
    with PiCamera(resolution=RESOLUTION) as camera:
        print('start')
        sleep(5)
        comm.Barrier()
        camera.capture('test.jpg')
            
        print('stop')
    
if __name__ == '__main__':
    main()
