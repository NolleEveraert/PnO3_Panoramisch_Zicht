from os import write
import numpy as np
from mpi4py import MPI
from picamera import PiCamera
import cv2 as cv
from time import time, sleep
from threading import Thread
# import multiprocessing as mp

from stream import Recorder, FrameBuffer, send, transform, receive, mergeFrames, RESOLUTION, FRAMERATE, stop, running
from projection import getTransformMatrices
# from server import app


LEFT_DICT = {
    'aperture_rad': 198 * np.pi/180,
    'radius': 1070/2592 * RESOLUTION[0],
    'center_x': 1160/2592 * RESOLUTION[0],
    'center_y': 957/1920 * RESOLUTION[1],
}

RIGHT_DICT = {
    'aperture_rad': 198 * np.pi/180,
    'radius': 1070/2592 * RESOLUTION[0],
    'center_x': 1257/2592 * RESOLUTION[0],
    'center_y': 940/1920 * RESOLUTION[1],
}


def write_times(time_list):
    res = f'{RESOLUTION[0]}x{RESOLUTION[1]}'
    with open(f'tijden/{FRAMERATE}-{res}.txt', 'w') as f:
        f.write(f'FPS: {FRAMERATE}\n')
        f.write(f'RESOLUTIE: {res}\n\n')
        for name, times in time_list:
            f.write(name)
            f.write('\n')
            f.write('\t'.join([str(time) for time in times]))
            f.write('\n\n')



def senderloop(camera, comm):
    global running

    matrixX, matrixY = getTransformMatrices(LEFT_DICT['aperture_rad'], LEFT_DICT['center_x'], LEFT_DICT['center_y'], LEFT_DICT['radius'])

    record_buffer = FrameBuffer()
    transform_buffer = FrameBuffer()

    transform_times = []
    send_times = []

    with Recorder(camera, record_buffer, comm) as recorder:
        camera.start_recording(recorder, 'bgr')
        begin = time()
        transform_thread = Thread(target=transform, args=(record_buffer, transform_buffer, matrixX, matrixY, transform_times))
#         transform_thread = mp.Process(target=transform, args=(record_buffer, transform_buffer))
        send_thread = Thread(target=send, args=(comm, transform_buffer, send_times))
        
        transform_thread.start()
        send_thread.start()
        sleep(10)
        stop()
        end = time()
        print(f'time {end-begin}')
        camera.stop_recording()

        send_thread.join()
        transform_thread.join()
        write_times([('send', send_times), ('transform', transform_times)])


# def senderloop(camera, comm):
#     sender = StreamSender(comm)
#     camera.start_recording(sender, 'mjpeg')
#     begin = time()
#     while True:
#         sender.send()
#         sleep(0.01)
#         if time() - begin > 10:
#             break
#     end = time()
#     print(f'time {end-begin}')
#     camera.stop_recording()
        
        
def receiverloop(camera, comm):

    # fourcc = cv.VideoWriter_fourcc('M', 'J', 'P', 'G')
    # out = cv.VideoWriter('output.avi', fourcc, 20.0, (RESOLUTION[0], RESOLUTION[1]), True)

    matrixX, matrixY = getTransformMatrices(RIGHT_DICT['aperture_rad'], RIGHT_DICT['center_x'], RIGHT_DICT['center_y'], RIGHT_DICT['radius'])


    record_buffer = FrameBuffer()
    receive_buffer = FrameBuffer()
    transform_buffer = FrameBuffer()
    merge_buffer = FrameBuffer()

    receive_times = []
    transform_times = []
    merge_times = []

    with Recorder(camera, record_buffer, comm) as recorder:
        camera.start_recording(recorder, 'bgr')
    
        receive_thread = Thread(target=receive, args=(comm, receive_buffer, receive_times))
        transform_thread = Thread(target=transform, args=(record_buffer, transform_buffer, matrixX, matrixY, transform_times))
        merge_thread = Thread(target=mergeFrames, args=(transform_buffer, receive_buffer, merge_buffer, merge_times))
    #     receive_thread = mp.Process(target=receive, args=(comm, receive_buffer))
    #     receive_thread.daemon = True
    #     transform_thread.daemon = True
    #     merge_thread.daemon = True
        receive_thread.start()
        transform_thread.start()
        merge_thread.start()
        while running:
            count, frame = merge_buffer.get()
            if count == None:
                break
            
    #             cv.imshow('merged', frame)
    #             cv.waitKey(100)
            
            # out.write(frame)
            # cv.imshow('merged', frame)
            sleep(0.1)
            # cv.imwrite(f'frames/frame{count}.jpg', frame)

        camera.stop_recording()
        # out.release()

        receive_thread.join()
        transform_thread.join()
        merge_thread.join()
        write_times([('receive', receive_times), ('transform', transform_times), ('merge', merge_times)])

    
    
    
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
    cv.waitKey(1)


def main():
    print('test')
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    #size = comm.Get_size()
    hostname = MPI.Get_processor_name()
       
    with PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
        print(f'start {rank}')
        comm.Barrier()
        print(f'{rank}: {time()}')
        if rank == 1:
            senderloop(camera, comm)
        elif rank == 0:
            receiverloop(camera, comm)

        print(f'stop {rank}')


if __name__ == '__main__':
    main()
