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


def takeimages(N, comm):
    images = []
    print('camera initialiseren')
    with PiCamera() as camera:
        sleep(1)
        for i in range(N):
            output = numpy.empty((HEIGHT,WIDTH,3),dtype=numpy.uint8)
            camera.resolution = (WIDTH, HEIGHT)
            comm.Barrier()
            camera.capture(output, 'bgr')
            print(f'captured {i}')
            images.append(output)
            sleep(0.1)
    return images
            
def stitch(images):
    print('Beginnen met stitching')
    #schaal = 1  # hoe hard wordt de foto veranderd
    
    stitcher = cv2.createStitcher()
    status, result = stitcher.stitch(images)

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
    # if rank == 0:
    #     comm.send(0, dest=1, tag=11)
    # elif rank == 1:
    #     comm.recv(source=0, tag=11)
    
    own_images = takeimages(1, comm)
    print('foto genomen from:' + str(hostname))
    if rank == 1:
        comm.Send(own_images,dest=0,tag=13)
        print('fotos verzonden from:' + str(hostname))
    elif rank == 0:
        other_images = numpy.empty((HEIGHT,WIDTH,3),dtype=numpy.uint8)
        comm.Recv(other_images, source=1,tag=13)
        print('fotos ontvangen')
        for i, own in enumerate(own_images):
            cv2.imwrite(f'outputs/own_photo{i+1}.jpg', own)
        for i, other in enumerate(other_images):
            cv2.imwrite(f'outputs/other_photo{i+1}.jpg', other)
        # stitch([foto1, foto2])
    
if __name__ == '__main__':
    main()