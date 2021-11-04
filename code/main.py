import numpy as np
from mpi4py import MPI
from picamera import PiCamera
import cv2 as cv
from time import time

from stream import Receiver, StreamRecorder, StreamSender

RESOLUTION = (1640,1232)
FRAMERATE = 15


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    #size = comm.Get_size()
    hostname = MPI.Get_processor_name()

    with PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
        if rank == 1:
            camera.start_recording(StreamSender(comm), 'mjpeg')
            camera.wait_recording(10)
        elif rank == 0:
            recorder = StreamRecorder(camera)
            camera.start_recording(recorder, 'mjpeg')
            recv = Receiver(comm)
            data = None
            own_image = np.empty((RESOLUTION[1], RESOLUTION[0], 3), dtype=np.uint8)
            while data != 'STOP':
                other_image = recv.read()
                print(f'received frame {recv.frame}')
                camera.capture(own_image)
                print('captured image')

        camera.stop_recording()


