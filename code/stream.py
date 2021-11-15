from picamera.array import PiRGBAnalysis
import numpy as np
import cv2 as cv
import io


class StreamSender(object):
    def __init__(self, comm):
        self.comm = comm
        self.stream = io.BytesIO()
        self.frame = 1
        
    def write(self, data):
        if data.startswith(b'\xff\xd8'):
            # byte code voor een nieuwe frame => stuur inhoud van buffer door met MPI 
            size = self.stream.tell()
            #print(f'sender: {self.frame}')
            if size > 0:
                self.stream.seek(0)
                
                
                if rank == 0:
                    comm.send(0, dest=1, tag=0)
                elif rank == 1:
                    comm.recv(source=0, tag=0)
                
                
                if rank == 1:
                    self.comm.send(self.stream.read(size), dest=0, tag=self.frame)
                elif rank == 0:
                    received_img = self.comm.recv(source=1,tag=self.frame)
                    print(self.frame)
                self.frame += 1
                self.stream.seek(0)
        self.stream.write(data)

    def flush(self):
        self.comm.send(np.empty(0), dest=0, tag=self.frame)


class StreamRecorder(PiRGBAnalysis):
    def __init__(self, camera):
        super().__init__(camera)
        self.frames = {}
        self.frame_count = 0

    def analyse(self, array):
        self.frames[self.frame_count] = array

    def get_frame(self, frame):
        return self.frames.pop(frame)


class Receiver:
    def __init__(self, comm):
        self.comm = comm
        self.frame = 0

    def read(self):
        data = self.comm.recv(source=1, tag=self.frame) # Als de streamer rank 1 heeft
        if len(data) == 0:
            return
        else:
            print(f'receiver: {self.frame}')
            self.frame += 1
            inp = np.frombuffer(data, np.uint8)
            image = cv.imdecode(inp, cv.IMREAD_COLOR)

            return image
    
