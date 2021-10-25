import numpy as np
import cv2
import time

img = cv2.imread(r'projections\fisheye-210.jpg')
APERTURE_RAD = 210 * np.pi/180
IMG_HEIGHT, IMG_WIDTH = img.shape[:2]
RADIUS = 1024
CENTER_X, CENTER_Y = 1024,1024+96

CANVAS_WIDTH = 720
CANVAS_HEIGHT = 500


def equirectToFishPolar(Xe, Ye):
    # x_norm and y_norm in [-1,1]
    x_norm = Xe * 2/CANVAS_WIDTH - 1
    y_norm = Ye * 2/CANVAS_HEIGHT - 1

    long = x_norm * np.pi
    lat = y_norm * np.pi/2

    Px = np.cos(lat) * np.cos(long)
    Py = np.cos(lat) * np.sin(long)
    Pz = np.sin(lat)

    r = 2 * np.arctan2(np.sqrt(Px**2 + Pz**2), Py) / APERTURE_RAD
    theta = np.arctan2(Pz, Px)

    return r, theta


def fishPolarToFishCart(r, theta):
    x = CENTER_X + r*RADIUS*np.cos(theta)
    y = CENTER_Y + r*RADIUS*np.sin(theta)

    return int(x), int(y)


def main():
    canvas = np.zeros((CANVAS_HEIGHT, CANVAS_WIDTH, 3), np.uint8)

    for Ye in range(CANVAS_HEIGHT):
        for Xe in range(CANVAS_WIDTH):
            r, theta = equirectToFishPolar(Xe, Ye)
            x,y = fishPolarToFishCart(r, theta)
            if 0 <= y < img.shape[0] and 0 <= x < img.shape[1]:
                canvas[Ye][Xe] = img[y][x]
    
    cv2.imwrite(r'projections\output.jpg', canvas)


if __name__ == '__main__':
    start = time.perf_counter()
    main()
    end = time.perf_counter()

    print(f"process finished in {end-start}s")