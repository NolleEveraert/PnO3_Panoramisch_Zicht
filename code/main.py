import numpy as np
from mpi4py import MPI
from picamera import PiCamera
import cv2 as cv
import time

from stream import Receiver, StreamRecorder, StreamSender

RESOLUTION = (1296,976)
FRAMERATE = 15


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    #size = comm.Get_size()
    hostname = MPI.Get_processor_name()
    
    #sync na MPI opstarten
    if rank == 0:
        comm.send(0, dest=1, tag=0)
    elif rank == 1:
        comm.recv(source=0, tag=0)
        print('MPI gesynchroniseerd')
    

    with PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
        print('start')
        frame_count = 1
        start =  time.perf_counter()
        while frame_count < 100:
            #sync voor elke frame
            if rank == 0:
                comm.send(0, dest=1, tag=0)
            elif rank == 1:
                comm.recv(source=0, tag=0)
                
                
            if rank == 1:
                #camera.start_recording(StreamSender(comm), 'mjpeg')
                #camera.wait_recording(10)
                #camera.stop_recording()
                current_frame = np.empty((RESOLUTION[1],RESOLUTION[0],3),dtype=np.uint8)
                camera.capture(current_frame, 'rgb', use_video_port=True)
                comm.send(current_frame, dest=0, tag=frame_count)
                
            
            elif rank == 0:
                #recorder = StreamRecorder(camera)
                #camera.start_recording(recorder, 'mjpeg')
                #recv = Receiver(comm)
                own_image = np.empty((RESOLUTION[1], RESOLUTION[0], 3), dtype=np.uint8)
                camera.capture(own_image, 'rgb', use_video_port=True)
                #data = recv.read()
                received_img = comm.recv(source=1, tag=frame_count)
                #if data is None:
                    #break
                #print(f'received frame {recv.frame}')
            frame_count +=1
            print(frame_count)
        end = time.perf_counter()
        tijd = end-start
        print(tijd)
        print('stop')


if __name__ == '__main__':
    main()
