import cv2
import os
from picamera import PiCamera
from time import sleep
import numpy


# mainFolder = "alle fotos"  # folder waar python code in staat
# mijnFolders = os.listdir(mainFolder)  # alle folders met fotos
# print(mijnFolders)

mainFolder = "alle fotos/"


def takephotos(AANTAL):
    WIDTH = 3280
    HEIGHT = 2464
    with PiCamera() as camera:
        camera.start_preview()
        print(AANTAL)
        for i in range(1, AANTAL + 1):
            print(i)
            wait = input('Enter om foto te nemen.')
            camera.resolution = (WIDTH, HEIGHT)
            camera.capture(f'{mainFolder}genomen fotos/image{str(i)}.jpg')
        camera.stop_preview()

def stitch():
    schaal = 1  # hoe hard wordt de foto veranderd
    i = 1
    pad = mainFolder + 'genomen fotos'
    fotos = []
    mijnLijst = os.listdir(pad)
    print(mijnLijst)
    print(f'Aantal fotos gedecteerd: {len(mijnLijst)}')  # formatted string
    for foto in mijnLijst:
        huidigeFoto = cv2.imread(f'{pad}/{foto}')
        huidigeFoto = cv2.resize(huidigeFoto, (0, 0), None, schaal, schaal)
        fotos.append(huidigeFoto)

    stitcher = cv2.createStitcher()
    status, result = stitcher.stitch(fotos)

    if status == cv2.STITCHER_OK:
        print("Panorama gemaakt")
        cv2.imwrite(f'{mainFolder}outputs/output{str(i)}.jpg', result)
        i += 1
        # cv2.imshow(f"Gestitchde foto: {folder}", result)
    else:
        print("Panorama gefaald")

    cv2.waitKey()

def main():
    takephotos(2)
    stitch()
    
main()