#
import numpy as np
from mpi4py import MPI
from picamera import PiCamera
from picamera.array import PiRGBAnalysis
import cv2 as cv
import io
from time import time
#import Projectiematrix

RESOLUTION = (1640,1232)
FRAMERATE = 15
    
#projectie berekenen
#map_x, map_y = Projectiematrix.getTransformMatrices()

class MyOutput(object):
    def __init__(self, comm):
        #super(MyOutput, self).__init__(camera)
        rank = comm.Get_rank()
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
    with PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
        output = MyOutput(comm)
        camera.start_recording(output, 'mjpeg')
        camera.wait_recording(10)
        #sleep(2)
        camera.stop_recording()


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    hostname = MPI.Get_processor_name()
    # sync MPI
    if rank == 0:
        comm.send(0, dest=1, tag=1000)
        comm.send(0,dest=2,tag=1001)
    elif rank == 1:
        comm.recv(source=0, tag=1000)    
    elif rank == 2:
        comm.recv(source=0,tag=1001)
        
    print('MPI gesyncroniseerd')    
    print(hostname +'  ' +str(rank)) 
    
    if rank == 1:
        record_video(comm)
#    if rank == 2:
        #record_video(comm)
    elif rank == 0:
        frame = 0
        #vorige = time()
        while True:
            #begin = time()
            data1 = comm.recv(source=1, tag=frame)
            data2 = comm.recv(source=2, tag=frame)
            print(f'receiver: {frame}')
            #fps = round(1.0 / (begin - vorige))
            #print(f'fps: {fps}')
            
            if len(data1) == 0:
                break
            else:
                print(f'receiver: {frame}')
                frame += 1
                inp1 = np.frombuffer(data1, np.uint8)
                image1 = cv.imdecode(inp1, cv.IMREAD_COLOR)
                inp2 = np.frombuffer(data2, np.uint8)
                image2 = cv.imdecode(inp2, cv.IMREAD_COLOR)
                #out.write(image)
                #cv.imshow('cam', image)
                #cv.waitKey(10)
            #vorige = begin
    
        #totale_tijd = time() - begin
        #gemiddeld_fps = frame / totale_tijd
        #print(f'gemiddeld fps: {gemiddeld_fps}')
        

        
        #out.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
    

