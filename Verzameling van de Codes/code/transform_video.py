import numpy as np
import cv2 as cv
from projection import getTransformMatrices, merge, perform_transform
from config import RIGHT_DICT, LEFT_DICT, CANVAS_WIDTH, CANVAS_HEIGHT

PATH_LEFT = ''
PATH_RIGHT = ''


def main():
    matrixX1, matrixY1 = getTransformMatrices(RIGHT_DICT['aperture_rad'], RIGHT_DICT['center_x'], RIGHT_DICT['center_y'], RIGHT_DICT['radius'], a_right=RIGHT_DICT['a_right_rad'], a_up=RIGHT_DICT['a_up_rad'])
    matrixX2, matrixY2 = getTransformMatrices(LEFT_DICT['aperture_rad'], LEFT_DICT['center_x'], LEFT_DICT['center_y'], LEFT_DICT['radius'], a_right=LEFT_DICT['a_right_rad'], a_up=LEFT_DICT['a_up_rad'])

    cap1 = cv.VideoCapture(PATH_LEFT)
    cap2 = cv.VideoCapture(PATH_RIGHT)

    out = cv.VideoWriter('output.avi', cv.VideoWriter_fourcc(*'XVID'), float(10), (CANVAS_WIDTH, CANVAS_HEIGHT))


    while(cap1.isOpened()):
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        tranformed1 = perform_transform(frame1, matrixX1, matrixY1)
        tranformed2 = perform_transform(frame2, matrixX2, matrixY2)

        merged = merge(tranformed1, tranformed2)
        out.write(merged)

    cap1.release()
    cap2.release()

if __name__ == '__main__':


    main()
    


