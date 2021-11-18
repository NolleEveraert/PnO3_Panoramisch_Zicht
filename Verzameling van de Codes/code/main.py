import numpy as np
from mpi4py import MPI
from picamera import PiCamera
import cv2 as cv
from time import time, sleep

from stream import Receiver, StreamRecorder, StreamSender, RESOLUTION, FRAMERATE


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    #size = comm.Get_size()
    hostname = MPI.Get_processor_name()

    with PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
        print('start')
        comm.Barrier()
        if rank == 1:
            sender = StreamSender(comm)
            camera.start_recording(sender, 'mjpeg')
            while True:
                sender.send()
                sleep(0.01)
            camera.stop_recording()
            
        elif rank == 0:
            with StreamRecorder(camera, comm) as recorder:
                camera.start_recording(recorder, 'rgb')
                recv = Receiver(comm)
                #own_image = np.empty((RESOLUTION[1], RESOLUTION[0], 3), dtype=np.uint8)
                
                while True:
                    data = recv.read()
                    own_image = recorder.get_frame()
                    if data is None:
                        print('stop recording')
                        camera.stop_recording()
                        print('stopped recording')
                        break

        print('stop')


if __name__ == '__main__':
    main()
