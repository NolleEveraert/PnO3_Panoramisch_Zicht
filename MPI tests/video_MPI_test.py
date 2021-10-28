import numpy as np
from mpi4py import MPI
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
import cv2 as cv
import io
from time import time


class MyOutput(object):
    def __init__(self, comm):
        #super(MyOutput, self).__init__(camera)
        self.comm = comm
        self.stream = io.BytesIO()
        self.frame = 0
        
    def write(self, data):
        if data.startswith(b'\xff\xd8'):
            size = self.stream.tell()
            print(f'sender: {self.frame}')
            if size > 0:
                self.stream.seek(0)
                self.comm.send(self.stream.read(size), dest=0, tag=self.frame)
                self.frame += 1
                self.stream.seek(0)
        self.stream.write(data)
        
    def flush(self):
        #print(f'{self.size} bytes written')
        self.comm.send(np.empty(0), dest=0, tag=self.frame)


def record_video(comm):
    with PiCamera(resolution='1640x1232', framerate=100) as camera:
        output = MyOutput(comm)
        camera.start_recording(output, 'mjpeg')
        camera.wait_recording(30)
        #sleep(2)
        camera.stop_recording()
        


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    hostname = MPI.Get_processor_name()
    
#sync voor foto nemen
    if rank == 0:
        comm.send(0, dest=1, tag=1000)
    elif rank == 1:
        comm.recv(source=0, tag=1000)
    
    if rank == 1:
        record_video(comm)
    elif rank == 0:
        frame = 0
        vorige = time()
        while True:
            begin = time()
            data = comm.recv(source=1, tag=frame)
            print(f'receiver: {frame}')
            fps = round(1.0 / (begin - vorige))
            print(f'fps: {fps}')
            
            if len(data) == 0:
                break
            else:
                print(f'receiver: {frame}')
                frame += 1
                inp = np.frombuffer(data, np.uint8)
                image = cv.imdecode(inp, cv.IMREAD_COLOR)
                #out.write(image)
                #cv.imshow('cam', image)
                #cv.waitKey(10)
            vorige = huidige

        
        totale_tijd = time() - begin
        gemiddeld_fps = frame / totale_tijd
        print(f'gemiddeld fps: {gemiddeld_fps}')
        #out.release()
        cv.destroyAllWindows()

if __name__ == '__main__':
    main()
    