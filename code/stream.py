from picamera import PiCamera
import numpy as np
import cv2 as cv
import io

RESOLUTION = (1640,1232)
FRAMERATE = 15


class Streamer(object):
    def __init__(self, comm):
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


class Receiver:
    def __init__(self, comm):
        self.comm = comm
        self.frame = 0

    def read(self):
        data = self.comm.recv(source=1, tag=self.frame) # Als de streamer rank 1 heeft
        if len(data) == 0:
            return 'STOP'
        else:
            print(f'receiver: {self.frame}')
            self.frame += 1
            inp = np.frombuffer(data, np.uint8)
            image = cv.imdecode(inp, cv.IMREAD_COLOR)

            return image


def record_video(output):
    with PiCamera(resolution=RESOLUTION, framerate=FRAMERATE) as camera:
        camera.start_recording(output, 'mjpeg')
        camera.wait_recording(10)
        camera.stop_recording()
