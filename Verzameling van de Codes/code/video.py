# synchroon video recorden

import numpy as np
from mpi4py import MPI
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
import cv2 as cv
from time import time, sleep

RESOLUTION =  (800,608)
FRAMERATE = 30

class Record_video(PiRGBAnalysis):
    def __init__(self, camera, comm):
        super().__init__(camera)
        self.frames = []
        self.frame_count = 1
        self.comm = comm

    def analyze(self, array):
        self.frames.append(array)
        self.comm.Barrier()
        self.frame_count += 1
        
    def get_frame(self):
        if len(self.frames) > 0:
            frame = self.frames.pop(0)
            return frame
        return None
    
    
    
def recorderloop(camera, comm):
    fourcc = cv.VideoWriter_fourcc(*'XVID')
    video = cv.VideoWriter('test.avi',fourcc, float(FRAMERATE), (RESOLUTION[0],RESOLUTION[1]))
    with Record_video(camera, comm) as recorder:
        comm.Barrier()
        camera.start_recording(recorder, 'rgb')
        camera.wait_recording(20)
        while True:
            frame = recorder.get_frame()
            if frame is not None:
                video.write(frame)
            else:
                break
             
        video.release()
            
    
def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    hostname = MPI.Get_processor_name()
    
    with PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
        print('start')
        comm.Barrier()
        
        if rank == 0:
            recorderloop(camera, comm)
            
        elif rank == 1:
            recorderloop(camera, comm)
            
        print('stop')
    
    
main()