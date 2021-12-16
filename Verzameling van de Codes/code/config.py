import numpy as np

DURATION = 60
RESOLUTION =  (800, 608)#(1296,976)
FRAMERATE = 5

CANVAS_WIDTH = 720 #1440
CANVAS_HEIGHT = 500 #1000
MARGIN = 0.03  

LEFT_DICT = {
    'aperture_rad': 195 * np.pi/180,
    'radius': 1070/2592 * RESOLUTION[0],
    'center_x': 1160/2592 * RESOLUTION[0],
    'center_y': 957/1920 * RESOLUTION[1],
    'a_right_rad': 0,
    'a_up_rad': 0,
}

RIGHT_DICT = {
    'aperture_rad': 197 * np.pi/180,
    'radius': 1070/2592 * RESOLUTION[0],
    'center_x': 1257/2592 * RESOLUTION[0],
    'center_y': 940/1920 * RESOLUTION[1],
    'a_right_rad': -2 * np.pi/180,
    'a_up_rad': 3 * np.pi/180,
}

