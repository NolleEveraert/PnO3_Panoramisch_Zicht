import numpy as np
from mpi4py import MPI
from picamera import PiCamera
import cv2 as cv
from time import time, sleep

from stream import Receiver, StreamRecorder, StreamSender

RESOLUTION = (1296,972)
FRAMERATE = 12


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    #size = comm.Get_size()
    hostname = MPI.Get_processor_name()

    with PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
        print('start')
        if rank == 1:
            camera.start_recording(StreamSender(comm), 'mjpeg')
            camera.wait_recording(10)
            camera.stop_recording()
            
        elif rank == 0:
            with StreamRecorder(camera, comm) as recorder:
                camera.start_recording(recorder, 'mjpeg')
                recv = Receiver(comm)
                #own_image = np.empty((RESOLUTION[1], RESOLUTION[0], 3), dtype=np.uint8)
                while True:
                    data = recv.read()
                    if data is None:
                        camera.stop_recording()
                        break
                    print(f'received frame {recv.frame}')
                    #camera.capture(own_image, 'rgb', use_video_port=True)
                    print('captured image')

                print('stop')


if __name__ == '__main__':
    main()
