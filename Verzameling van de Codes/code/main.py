from os import write
import numpy as np
from mpi4py import MPI
from picamera import PiCamera
import cv2 as cv
from time import time, sleep
from threading import Thread

from stream import Recorder, FrameBuffer, send, transform, receive, mergeFrames, RESOLUTION, FRAMERATE, stop, running
from webstream import start_server
from projection import getTransformMatrices


DURATION = 60

LEFT_DICT = {
    'aperture_rad': 195 * np.pi/180,
    'radius': 1070/2592 * RESOLUTION[0],
    'center_x': 1160/2592 * RESOLUTION[0],
    'center_y': 957/1920 * RESOLUTION[1],
}

RIGHT_DICT = {
    'aperture_rad': 197 * np.pi/180,
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
    global running # TODO: nog nodig?

    matrixX, matrixY = getTransformMatrices(LEFT_DICT['aperture_rad'], LEFT_DICT['center_x'], LEFT_DICT['center_y'], LEFT_DICT['radius'])

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
        server_thread = Thread(target=start_server, args=(('', 8000), merge_buffer))
        receive_thread.start()
        transform_thread.start()
        merge_thread.start()
        server_thread.start()

        sleep(DURATION)
        camera.stop_recording()

        receive_thread.join()
        transform_thread.join()
        merge_thread.join()
        write_times([('receive', receive_times), ('transform', transform_times), ('merge', merge_times)])


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
