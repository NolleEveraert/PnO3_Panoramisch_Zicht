from picamera.array import PiRGBAnalysis
import numpy as np
import cv2 as cv
import io
from time import sleep
from threading import Thread

RESOLUTION =  (800,608)#(1296,976)
FRAMERATE = 1


class StreamSender(object):
    def __init__(self, comm):
        self.comm = comm
        self.stream = io.BytesIO()
        self.frame = 1
        self.frames_sent = 1
        self.frames = {}
        
    def write(self, data):
        if data.startswith(b'\xff\xd8'):
            # byte code voor een nieuwe frame => stuur inhoud van buffer door met MPI 
            size = self.stream.tell()
            if size > 0:
                self.stream.seek(0)
                self.frames[self.frame] = self.stream.read(size)
                print(f'sender: {self.frame} taken')
                self.frame += 1
                self.stream.seek(0)
                self.comm.Barrier()
        self.stream.write(data)
        
    def send(self):
        try:
            self.comm.send(self.frames.pop(self.frames_sent), dest=0, tag=self.frames_sent)
            print(f'sender: {self.frames_sent} sent')
            self.frames_sent += 1
        except KeyError:
            return

    def flush(self):
        print('flush')
        self.comm.send(b'10', dest=0, tag=self.frame)
        sleep(1)
        self.comm.Barrier()
        print('flushed')


class StreamRecorder(PiRGBAnalysis):
    def __init__(self, camera, comm):
        super().__init__(camera)
        self.frames = []
        self.frame_count = 1
        self.comm = comm

    def analyze(self, array):
        self.frames.append(array)
        print(f'receiver: {self.frame_count} taken')
        self.comm.Barrier()
        self.frame_count += 1
        

    def get_frame(self):
        if len(self.frames) > 0:
            return self.frames.pop(0)
        return None


class Receiver:
    def __init__(self, comm):
        self.comm = comm
        self.frame = 1

    def read(self):
        data = self.comm.recv(source=1, tag=self.frame) # Als de streamer rank 1 heeft
        if data == b'10':
            print('stop code ontvangen')
            return
        else:
            print(f'receiver: {self.frame} received')
            image = np.empty((RESOLUTION[1], RESOLUTION[0], 3))
            t = Thread(target=decode, args=(data, image, self.frame))
            t.start()
            t.join()
            self.frame += 1
            return image
        
        
def decode(data, image, frame):
    inp = np.frombuffer(data, np.uint8)
    image = cv.imdecode(inp, cv.IMREAD_COLOR)
    print(f'decoded: {frame}')
    
