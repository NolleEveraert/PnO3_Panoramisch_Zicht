from picamera.array import PiRGBAnalysis
import numpy as np
import cv2 as cv
from time import sleep, time

from projection import perform_transform, merge

RESOLUTION =  (800, 608)#(1296,976)
FRAMERATE = 5
running = True


# def loop(f, *args, **kwargs):
#     times = []
#     while running:
#         start = time()
#         f(args, kwargs)
#         times.append(time() - start)

#     return times



class FrameBuffer:
    def __init__(self, size=10):
        self.size = size
        self.frames = []
        
    def push(self, count, frame):
        self.frames.append((count, frame))
        if len(self.frames) > self.size:
            self.frames.pop(0)
    
    def get(self):
        global running
        while len(self.frames) == 0:
            if not running:
                return None, None
            sleep(0.01)

        return self.frames.pop(0)


class Recorder(PiRGBAnalysis):
    def __init__(self, camera, buffer, comm):
        super().__init__(camera)
        self.buffer = buffer
        self.frame_count = 1
        self.comm = comm
        self.rank = comm.Get_rank()

    def analyze(self, array):
        self.buffer.push(self.frame_count, array)
        print(f'{self.rank}: {self.frame_count} taken')
        self.comm.Barrier()
        self.frame_count += 1
        
        
def send(comm, buffer, times):
    global running
    print('started sending')
    frames_sent = 1
    while running:
        count, frame = buffer.get()

        start = time()
        if count != None:
            comm.send((count, frame), dest=0, tag=frames_sent)
            print(f'sent {count}')
            frames_sent += 1
        
        times.append(time() - start)

    comm.send((0, np.empty((1,1))), dest=0, tag=frames_sent)
        
        
def transform(inputBuffer, outputBuffer, matrixX, matrixY, times):
    global running

    print('started transforming')
    while running:
        count, frame = inputBuffer.get()
        
        start = time()
        if count != None:
            transformed = perform_transform(frame, matrixX, matrixY)
            outputBuffer.push(count, transformed)
            print(f'transformed {count}')

        times.append(time() - start)

    return times


def receive(comm, buffer, times):
    global running
    
    frames_received = 1
    while running:
        start = time()
        count, frame = comm.recv(source=1, tag=frames_received) # Als de streamer rank 1 heeft
        if count == 0:
            print('stop code ontvangen')
            running = False
            break
        else:
            buffer.push(count, frame)
            print(f'receiver: {frames_received} received')
            frames_received += 1
        times.append(time() - start)
    
    return times
        

def mergeFrames(buffer_in_1, buffer_in_2, buffer_out, times):
    while running:
        count1, frame1 = buffer_in_1.get()
        count2, frame2 = buffer_in_2.get()
        
        start = time()
        while count1 != count2:
            print(count1, count2)
            if count1 < count2:
                print(f'frame {count1} DROPPED')
                count1, frame1 = buffer_in_1.get()
            else:
                print(f'frame {count2} DROPPED')
                count2, frame2 = buffer_in_2.get()

        merged = merge(frame1, frame2)
        buffer_out.push(count1, merged)
        print(f'MERGED {count1}')
        times.append(time() - start)

    return times


def stop():
    global running
    running = False
