import cv2
import os
from picamera import PiCamera
from time import sleep
import numpy


# mainFolder = "alle fotos"  # folder waar python code in staat
# mijnFolders = os.listdir(mainFolder)  # alle folders met fotos
# print(mijnFolders)




def takephotos(AANTAL):
    WIDTH = 1600
    HEIGHT = 800
    with PiCamera() as camera:
        camera.start_preview()
        for i in range(1, AANTAL + 1):
            camera.resolution = (WIDTH, HEIGHT)
            camera.capture('image' + str(i) + '.jpg')
            # sleep(5)
            wait = input('Enter om verder te gaan.')
        camera.stop_preview()

def stitch():
    takephotos(5)
    schaal = 1  # hoe hard wordt de foto veranderd
    i = 1
    mainFolder = "alle fotos"  # folder waar python code in staat
    pad = mainFolder#+ "/" + folder
    fotos = []
    mijnLijst = os.listdir(pad)
    print(f'Aantal fotos gedecteerd: {len(mijnLijst)}')  # formatted string
    for foto in mijnLijst:
        huidigeFoto = cv2.imread(f'{pad}/{foto}')
        huidigeFoto = cv2.resize(huidigeFoto, (0, 0), None, schaal, schaal)
        fotos.append(huidigeFoto)

    stitcher = cv2.Stitcher.create()
    status, result = stitcher.stitch(fotos)

    if status == cv2.STITCHER_OK:
        print("Panorama gemaakt")
        cv2.imwrite('output'+str(i)+'.jpg', result)
        i += 1
        # cv2.imshow(f"Gestitchde foto: {folder}", result)
    else:
        print("Panorama gefaald")

    cv2.waitKey()

def main():
    takephotos(5)
    stitch()