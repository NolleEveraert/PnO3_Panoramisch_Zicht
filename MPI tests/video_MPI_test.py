import numpy as np
from mpi4py import MPI
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
import cv2 as cv

motion_dtype = np.dtype([
    ('x', 'i1'),
    ('y', 'i1'),
    ('sad', 'u2')
    ])


class MyOutput(PiRGBAnalysis):
    def __init__(self, camera, comm):
        super(MyOutput, self).__init__(camera)
        self.size = 0
        self.comm = comm
        self.frame = 0
        
    def analyze(self, s):
        self.size += len(s)
        
        self.comm.send(s.flatten(), dest=0, tag=self.frame)
        self.frame += 1
        
    def flush(self):
        print(f'{self.size} bytes written')
        #self.comm.send(np.empty(0), dest=0, tag=1)


def record_video(comm):
    with PiCamera() as camera:
        camera.resolution = (640,480)
        camera.framerate = 30
        camera.start_recording(MyOutput(camera, comm), 'rgb')
        camera.wait_recording(10)
        camera.stop_recording()

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    hostname = MPI.Get_processor_name()
    
    if rank == 1:
        record_video(comm)
    elif rank == 0:
        i = 0
        while True:
            data = comm.recv(source=1, tag=i)
            i += 1
            print(data)
            if len(data) == 0:
                break
            else:
                cv.imshow('cam', data.reshape((480,640)))
                
        
        cv.destroyAllWindows()

if __name__ == '__main__':
    main()
    