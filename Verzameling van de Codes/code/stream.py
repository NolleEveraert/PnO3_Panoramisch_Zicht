from picamera.array import PiRGBAnalysis
import numpy as np
import cv2 as cv
import io
from time import sleep
from threading import Thread

from projection import getTransformMatrices, perform_transform, merge

RESOLUTION =  (800,608)#(1296,976)
FRAMERATE = 10
running = True

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

matrixLeftx, matrixLefty = getTransformMatrices(LEFT_DICT['aperture_rad'], LEFT_DICT['center_x'], LEFT_DICT['center_y'], LEFT_DICT['radius'])
matrixRightx, matrixRighty = getTransformMatrices(RIGHT_DICT['aperture_rad'], RIGHT_DICT['center_x'], RIGHT_DICT['center_y'], RIGHT_DICT['radius'])


class FrameBuffer:
    def __init__(self, size=10):
        self.size = 10
        self.frames = []
        
    def push(self, count, frame):
        self.frames.append((count, frame))
        if len(self.frames) > self.size:
            self.frames.pop(0)
    
    def get(self):
        while len(self.frames) == 0:
            sleep(0.01)

        return self.frames.pop(0)
        # else:
        #     return None, None


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
        
        
def send(comm, buffer):
    print('started sending')
    frames_sent = 1
    while running:
        count, frame = buffer.get()
        if count != None:
            print(f'sending frame {frames_sent}')
            comm.send((count, frame), dest=0, tag=frames_sent)
            print(f'sent {count}')
            frames_sent += 1
        else:
            sleep(0.01)
            
    comm.send((0, np.empty()), dest=0, tag=frames_sent)
        
        
def transform(inputBuffer, outputBuffer):
    print('started transforming')
    while running:
        count, frame = inputBuffer.get()
        if count != None:
            print(f'transforming frame {count}')
            transformed = perform_transform(frame, matrixRightx, matrixRighty)
            outputBuffer.push(count, transformed)
            print(f'transformed {count}')
        else:
            sleep(0.01)


def receive(comm, buffer):
    global running
    print(running)
    frames_received = 1
    while running:
        print('receiving')
        count, frame = comm.recv(source=1, tag=frames_received) # Als de streamer rank 1 heeft
        if count == 0:
            print('stop code ontvangen')
            running = False
            break
        else:
            buffer.push(count, frame)
            print(f'receiver: {frames_received} received')
            frames_received += 1
        

def mergeFrames(buffer_in_1, buffer_in_2, buffer_out):
    while running:
        count1, frame1 = buffer_in_1.get()
        count2, frame2 = buffer_in_2.get()

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
        
        
# class Sender:
#     def __init__(self, comm, buffer):
#         self.comm = comm
#         self.buffer = buffer
#         
#     def send(self):
#         count, frame = self.buffer.get()
#         self.comm.send(frame, dest=0, tag=count)
        
#     def send(self):
#         data = self.buffer.get()
#         data = perform_transform(data, matrixRightx, matrixRighty)
#         self.comm.send(data, dest=0, tag=self.frames_sent)
#         self.frames_sent +=1
#         return None

# class StreamSender(object):
#     def __init__(self, comm):
#         self.comm = comm
#         self.stream = io.BytesIO()
#         self.frame = 1
#         self.frames_sent = 1
#         self.frames = {}
        
#     def write(self, data):
#         if data.startswith(b'\xff\xd8'):
#             # byte code voor een nieuwe frame => stuur inhoud van buffer door met MPI 
#             size = self.stream.tell()
#             if size > 0:
#                 self.stream.seek(0)
#                 self.frames[self.frame] = self.stream.read(size)
#                 print(f'sender: {self.frame} taken')
#                 self.frame += 1
#                 self.stream.seek(0)
#                 self.comm.Barrier()
#         self.stream.write(data)
        
#     def send(self):
#         try:
#             self.comm.send(self.frames.pop(self.frames_sent), dest=0, tag=self.frames_sent)
#             print(f'sender: {self.frames_sent} sent')
#             self.frames_sent += 1
#         except KeyError:
#             return

#     def flush(self):
#         print('flush')
#         self.comm.send(b'10', dest=0, tag=self.frame)
#         sleep(1)
#         self.comm.Barrier()
#         print('flushed')


# class StreamRecorderRecv(PiRGBAnalysis):
#     def __init__(self, camera, comm):
#         super().__init__(camera)
#         self.frames = []
#         self.frame_count = 1
#         self.comm = comm

#     def analyze(self, array):
#         self.frames.append(array)
#         print(f'receiver: {self.frame_count} taken')
#         self.comm.Barrier()
#         self.frame_count += 1
        

#     def get_frame(self):
#         if len(self.frames) > 0:
#             frame = self.frames.pop(0)
#             frame = perform_transform(frame, matrixLeftx, matrixLefty)
#             return frame
#         return None


# def mergeFrames():
    #     while count1 == None:
    #         count1, frame1 = buffer_in_1.get()
    #     while count2 == None:
    #         count2, frame2 = buffer_in_2.get()
    #     while count1 != None and count2 != None:
    #         if count2 > count1:
    #             count1, frame1 = buffer_in_1.get()
    #         elif count2 < count1:
    #             count2, frame2 = buffer_in_2.get()
    #         else:
    #             frame_out = merge(frame1, frame2)
    #             buffer_out.push(count1, frame_out)
    #             print(f'MERGED {count1}')
    #             break
        
        
            


# class Receiver:
#     def __init__(self, comm):
#         self.comm = comm
#         self.frame = 1
# 
#     def read(self):
#         #data = np.empty((RESOLUTION[1], RESOLUTION[0], 3))
#         data = self.comm.recv(source=1, tag=self.frame) # Als de streamer rank 1 heeft
#         if data == b'stop':
#             print('stop code ontvangen')
#             return
#         else:
#             print(f'receiver: {self.frame} received')
#             #image = np.empty((RESOLUTION[1], RESOLUTION[0], 3))
# #             t = Thread(target=decode, args=(data, image, self.frame))
# #             t.start()
# #             t.join()
#             self.frame += 1
#             return data
        
        
        

        
# def decode(data, image, frame):
#     inp = np.frombuffer(data, np.uint8)
#     image = cv.imdecode(inp, cv.IMREAD_COLOR)
#     perform_transform(image, matrixLeftx, matrixLefty)
    
#     print(f'decoded: {frame}')
    