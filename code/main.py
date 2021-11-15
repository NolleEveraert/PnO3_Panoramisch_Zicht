import numpy as np
from mpi4py import MPI
from picamera import PiCamera
import cv2 as cv
import time
from io import BytesIO
from picamera.array import PiRGBAnalysis

from stream import Receiver, StreamRecorder, StreamSender

RESOLUTION = (1296,976)
FRAMERATE = 30
SHUTTER_SPEED = 25*1000


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    #size = comm.Get_size()
    hostname = MPI.Get_processor_name()
    
    #sync na MPI opstarten
    comm.Barrier()
    

    with PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
        camera.shutter_speed = SHUTTER_SPEED
        print('start')
        frame_count = 1

        #frame_stream = BytesIO()
        frame_array = np.empty((RESOLUTION[1],RESOLUTION[0],3),dtype=np.uint8)
        
        if rank == 0:
            start =  time.perf_counter()
            camera.capture(frame_array,'rgb', use_video_port=True)
            end_foto = time.perf_counter()
            tijd_foto = end_foto - start
            print(tijd_foto)
            

        while frame_count < 100:
            
            #sync voor elke frame
            comm.Barrier()
            
            if rank == 1:
                #camera.start_recording(StreamSender(comm), 'mjpeg')
                #camera.wait_recording(20)
                #camera.stop_recording()
                #current_frame = np.empty((RESOLUTION[1],RESOLUTION[0],3),dtype=np.uint8)
                camera.capture(frame_array, 'rgb', use_video_port=True)
                comm.send(frame_array, dest=0, tag=frame_count)
                
            
            elif rank == 0:
                #recorder = StreamRecorder(camera)
                #camera.start_recording(recorder, 'mjpeg')
                #recv = Receiver(comm)
                
                camera.capture(frame_array, 'rgb', use_video_port=True)
                
                #data = recv.read()
                received_img = comm.recv(source=1, tag=frame_count)
                #if data is None:
                    #break
                #print(f'received frame {recv.frame}')
                print(frame_count)
            frame_count +=1
            
        if rank == 0:
            end = time.perf_counter()
            tijd = end-start
            print(tijd)
        
        print('stop')


if __name__ == '__main__':
    main()
