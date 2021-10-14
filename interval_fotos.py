from picamera import PiCamera
from time import sleep
import numpy

WIDTH = 1600
HEIGHT = 800


with PiCamera() as camera:
    camera.start_preview()
    for i in range(1,6):
        camera.resolution = (WIDTH, HEIGHT)
        #camera.capture('images/imagetest'+str(i)+'.jpg')
        sleep(1)
    camera.stop_preview()
    
