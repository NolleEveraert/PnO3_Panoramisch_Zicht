print('test voor import')
import numpy
#import mpi4py
from mpi4py import MPI

import cv2
#import os
from picamera import PiCamera
from time import sleep

print('test na MPI initialisatie')

WIDTH = 2592
HEIGHT = 1920


def takephotos():
    with PiCamera() as camera:
        #sleep(1)
        output = numpy.empty((HEIGHT,WIDTH,3),dtype=numpy.uint8)
        camera.resolution = (WIDTH, HEIGHT)
        camera.capture(output, 'bgr')
    return output
            
def stitch(fotos):
    print('Beginnen met stitching')
    #schaal = 1  # hoe hard wordt de foto veranderd
    
    stitcher = cv2.createStitcher()
    status, result = stitcher.stitch(fotos)

    if status == cv2.STITCHER_OK:
        print("Panorama gemaakt")
        cv2.imwrite(f'outputs/panorama.jpg', result)
        # cv2.imshow(f"Gestitchde foto: {folder}", result)
    else:
        print("Panorama gefaald")

    cv2.waitKey()
            
def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    hostname = MPI.Get_processor_name()
    
    #sync voor foto nemen
    if rank == 0:
        comm.send(0, dest=1, tag=11)
    elif rank == 1:
        comm.recv(source=0, tag=11)
    
    foto1 = takephotos()
    print('foto genomen from:' + str(hostname))
    if rank == 1:
        comm.Send(foto1,dest=0,tag=13)
        print('foto verzonden from:' + str(hostname))
    elif rank == 0:
        foto2 = numpy.empty((HEIGHT,WIDTH,3),dtype=numpy.uint8)
        comm.Recv(foto2, source=1,tag=13)
        print('foto ontvangen')
        cv2.imwrite(f'outputs/foto1.jpg', foto1)
        cv2.imwrite(f'outputs/foto2.jpg', foto2)
        stitch([foto1, foto2])
    
if __name__ == '__main__':
    main()