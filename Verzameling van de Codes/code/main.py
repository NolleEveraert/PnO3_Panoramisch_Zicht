import numpy as np
from mpi4py import MPI
from picamera import PiCamera
import cv2 as cv
from time import time, sleep
from threading import Thread
import multiprocessing as mp

from stream import Recorder, FrameBuffer, send, transform, RESOLUTION, FRAMERATE, running, receive, mergeFrames

def senderloop2(camera, comm):
    record_buffer = FrameBuffer()
    transform_buffer = FrameBuffer()
    with Recorder(camera, record_buffer, comm) as recorder:
        camera.start_recording(recorder, 'rgb')
        begin = time()
        transform_thread = Thread(target=transform, args=(record_buffer, transform_buffer))
#         transform_thread = mp.Process(target=transform, args=(record_buffer, transform_buffer))
        send_thread = Thread(target=send, args=(comm, transform_buffer))
        
        transform_thread.start()
        send_thread.start()
        sleep(10)
        running = False
        end = time()
        print(f'time {end-begin}')
        camera.stop_recording()

def senderloop(camera, comm):
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
        
        
def receiverloop(camera, comm):
#     fourcc = cv.VideoWriter_fourcc(*'MJPG')
#     out = cv.VideoWriter('output.avi', fourcc, 20.0, (RESOLUTION[0], RESOLUTION[1]), True)
#     
    record_buffer = FrameBuffer()
    receive_buffer = FrameBuffer()
    transform_buffer = FrameBuffer()
    merge_buffer = FrameBuffer()
    recorder = Recorder(camera, record_buffer, comm)
    
    camera.start_recording(recorder, 'rgb')
    
    receive_thread = Thread(target=receive, args=(comm, receive_buffer))
    transform_thread = Thread(target=transform, args=(record_buffer, transform_buffer))
    merge_thread = Thread(target=mergeFrames, args=(transform_buffer, receive_buffer, merge_buffer))
#     receive_thread = mp.Process(target=receive, args=(comm, receive_buffer))
#     receive_thread.daemon = True
#     transform_thread.daemon = True
#     merge_thread.daemon = True
    receive_thread.start()
    transform_thread.start()
    merge_thread.start()
    while running:
        count, frame = merge_buffer.get()
        if count != None:
            cv.imwrite(f'frames/frame{count}.jpg', frame)
        else:
            sleep(0.1)
    
    
#     receive_thread.join()
#     i = 0
#     while i < 1000:
#         _, own = record_buffer.get()
#         _, other = receive_buffer.get()
# #         out.write(other)
# #         ShowImages(other, own)
#         sleep(0.01)
#         i += 1
        



def ShowImages(other_image, own_image):
    cv.imshow('andere', other_image)
    cv.imshow('eigen', own_image)
#     cv.waitKey(1)

def main():
    print('test')
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    #size = comm.Get_size()
    hostname = MPI.Get_processor_name()
       
    with PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
        print(f'start {rank}')
        comm.Barrier()
        if rank == 1:
            senderloop2(camera, comm)
        elif rank == 0:
            receiverloop(camera, comm)

        print(f'stop {rank}')


if __name__ == '__main__':
    main()
