import numpy as np
from mpi4py import MPI
from picamera import PiCamera
import cv2 as cv
from time import time, sleep

from stream import Receiver, StreamRecorder, StreamSender, RESOLUTION, FRAMERATE


def senderloop(camera):  
    sender = StreamSender(comm)
    camera.start_recording(sender, 'mjpeg')
    begin = time()
    while True:
        sender.send()
        sleep(0.01)
        if time() - begin > 10:
            break
    end = time()
    print(f'time {end-begin}')
    camera.stop_recording()
        
        
def receiverloop():
    with StreamRecorder(camera, comm) as recorder:
        camera.start_recording(recorder, 'rgb')
        recv = Receiver(comm)
        #own_image = np.empty((RESOLUTION[1], RESOLUTION[0], 3), dtype=np.uint8)
        
        while True:
            own_image = recorder.get_frame()
            sleep(0.01)
            if own_image is not None:
                data = recv.read()
                sleep(0.1)
                #cv.imshow('andere', data)
                #cv.imshow('eigen', own_image)
                #cv.waitKey(0)
                if data is None:
                    print('stop recording')
                    camera.stop_recording()
                    print('stopped recording')
                    break


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    #size = comm.Get_size()
    hostname = MPI.Get_processor_name()

    with PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
        print('start')
        comm.Barrier()
        if rank == 1:
            senderloop(camera)
        elif rank == 0:
            receiverloop(camera)

        print('stop')


if __name__ == '__main__':
    main()
