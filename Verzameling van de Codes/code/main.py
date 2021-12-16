from os import write
import numpy as np
from mpi4py import MPI
from picamera import PiCamera
import cv2 as cv
from time import time, sleep
from threading import Thread

from stream import Recorder, FrameBuffer, send, transform, receive, mergeFrames, RESOLUTION, FRAMERATE, stop
from webstream import start_server
from projection import getTransformMatrices
from config import DURATION, LEFT_DICT, RIGHT_DICT, CANVAS_WIDTH, CANVAS_HEIGHT


def write_times(time_list):
    res = f'{RESOLUTION[0]}x{RESOLUTION[1]}'
    canvas = f'{CANVAS_WIDTH}x{CANVAS_HEIGHT}'
    with open(f'tijden/{FRAMERATE}-{res}-{canvas}.txt', 'w') as f:
        f.write(f'FPS: {FRAMERATE}\n')
        f.write(f'CAMERA RESOLUTIE: {res}\n')
        f.write(f'CANVAS RESOLUTIE: {canvas}\n')
        f.write(f'DUUR: {DURATION}s\n\n')
        for name, times in time_list:
            f.write(name)
            f.write('\n')
            f.write(f'{sum(times)/len(times)}\n')
            f.write(','.join([str(time) for time in times]))
            f.write('\n\n')



def senderloop(camera, comm):
    matrixX, matrixY = getTransformMatrices(LEFT_DICT['aperture_rad'], LEFT_DICT['center_x'], LEFT_DICT['center_y'], LEFT_DICT['radius'], a_right=LEFT_DICT['a_right_rad'], a_up=LEFT_DICT['a_up_rad'])

    record_buffer = FrameBuffer()
    transform_buffer = FrameBuffer()

    transform_times = []
    send_times = []

    with Recorder(camera, record_buffer, comm) as recorder:
        camera.start_recording(recorder, 'bgr')

        transform_thread = Thread(target=transform, args=(record_buffer, transform_buffer, matrixX, matrixY, transform_times))
        send_thread = Thread(target=send, args=(comm, transform_buffer, send_times))
        transform_thread.start()
        send_thread.start()

        sleep(DURATION)
        stop()

        camera.stop_recording()
        send_thread.join()
        transform_thread.join()
        write_times([('send', send_times), ('transform', transform_times)])
        
        
def receiverloop(camera, comm):

    matrixX, matrixY = getTransformMatrices(RIGHT_DICT['aperture_rad'], RIGHT_DICT['center_x'], RIGHT_DICT['center_y'], RIGHT_DICT['radius'], a_right=RIGHT_DICT['a_right_rad'], a_up=RIGHT_DICT['a_up_rad'])


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
        server_thread = Thread(target=start_server, args=(('', 8000), merge_buffer))
        receive_thread.start()
        transform_thread.start()
        merge_thread.start()
        server_thread.start()

        #sleep(DURATION)
        

        receive_thread.join()
        transform_thread.join()
        merge_thread.join()
        write_times([('receive', receive_times), ('transform', transform_times), ('merge', merge_times)])

        camera.stop_recording()


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
       
    with PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
        print(f'start {rank}')
        comm.Barrier()
        if rank == 1:
            senderloop(camera, comm)
        elif rank == 0:
            receiverloop(camera, comm)

        print(f'stop {rank}')


if __name__ == '__main__':
    main()
