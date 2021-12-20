import numpy as np
import cv2 as cv
from numpy.core.fromnumeric import transpose
from projection import getTransformMatrices, merge, perform_transform
from config import CANVAS_WIDTH, CANVAS_HEIGHT

PATH_LEFT = 'test1640012516.avi'
PATH_RIGHT = '01-test1640012516.avi'

width = 800
height = 608

LEFT_DICT = {
    'aperture_rad': 195 * np.pi/180,
    'radius': 1070/2592 * width,
    'center_x': 1160/2592 * width,
    'center_y': 957/1920 * height,
    'a_right_rad': 0,
    'a_up_rad': 0,
}

RIGHT_DICT = {
    'aperture_rad': 197 * np.pi/180,
    'radius': 1070/2592 * width,
    'center_x': 1257/2592 * width,
    'center_y': 940/1920 * height,
    'a_right_rad': -2 * np.pi/180,
    'a_up_rad': 3 * np.pi/180,
}



def main():
    matrixX1, matrixY1 = getTransformMatrices(RIGHT_DICT['aperture_rad'], RIGHT_DICT['center_x'], RIGHT_DICT['center_y'], RIGHT_DICT['radius'], a_right=RIGHT_DICT['a_right_rad'], a_up=RIGHT_DICT['a_up_rad'])
    matrixX2, matrixY2 = getTransformMatrices(LEFT_DICT['aperture_rad'], LEFT_DICT['center_x'], LEFT_DICT['center_y'], LEFT_DICT['radius'], a_right=LEFT_DICT['a_right_rad'], a_up=LEFT_DICT['a_up_rad'])

    cap1 = cv.VideoCapture(PATH_RIGHT)
    cap2 = cv.VideoCapture(PATH_LEFT)

    out = cv.VideoWriter('output.avi', cv.VideoWriter_fourcc(*'XVID'), float(10), (CANVAS_WIDTH, CANVAS_HEIGHT))

    count = 1
    while(cap1.isOpened() and cap2.isOpened()):
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()
        
        transformed1 = perform_transform(frame1, matrixX1, matrixY1)
        transformed2 = perform_transform(frame2, matrixX2, matrixY2)

        merged = merge(transformed2, transformed1).astype(np.uint8)
        
        out.write(merged)
        print(f'merged {count}')
        count += 1

    cap1.release()
    cap2.release()

if __name__ == '__main__':


    main()
    


