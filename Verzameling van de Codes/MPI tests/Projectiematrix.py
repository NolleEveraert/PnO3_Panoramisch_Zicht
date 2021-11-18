import numpy as np
import cv2
import time

#img = cv2.imread('Projections/fisheye-210.jpg')
APERTURE_RAD = 210 * np.pi/180
IMG_HEIGHT, IMG_WIDTH = img.shape[:2]
RADIUS = 1024
CENTER_X, CENTER_Y = 1024,1024+96

CANVAS_WIDTH = 720
CANVAS_HEIGHT = 500


"""
Berekent matrices map_x en map_y die specifieren voor elke pixel in de output image, waar die pixel vandaan komt in de input image (fisheye).
Deze moeten 1 keer berekend worden, en blijven daarna voor de rest van de executie hetzelfde.
"""
def getTransformMatrices():
    # de oorspronkelijke coordinaten van elke pixel
    # Xe[y,x] = x; Ye[y,x] = y
    Xe = np.tile(np.arange(CANVAS_WIDTH, dtype=np.float32), (CANVAS_HEIGHT,1))
    Ye = np.tile(np.arange(CANVAS_HEIGHT, dtype=np.float32).reshape((CANVAS_HEIGHT, 1)), (1,CANVAS_WIDTH))

    # x_norm and y_norm in [-1,1]
    x_norm = Xe * 2/CANVAS_WIDTH - 1
    y_norm = Ye * 2/CANVAS_HEIGHT - 1

    # lengtegraad en breedtegraad van elke pixel
    long = x_norm * np.pi
    lat = y_norm * np.pi/2

    # 3D coordinaten van elke pixel (op een boloppervlak)
    Px = np.cos(lat) * np.cos(long)
    Py = np.cos(lat) * np.sin(long)
    Pz = np.sin(lat)

    # polaire coordinaten op de fisheye image
    r = 2 * np.arctan2(np.sqrt(Px*Px + Pz*Pz), Py) / APERTURE_RAD
    theta = np.arctan2(Pz, Px)

    # reele cartesische coordinaten op de fisheye image
    map_x = CENTER_X + r*RADIUS*np.cos(theta)
    map_y = CENTER_Y + r*RADIUS*np.sin(theta)

    return map_x, map_y


def perform_transform(map_x, map_y):

    canvas = cv2.remap(img, map_x, map_y, interpolation=cv2.INTER_LINEAR)

    # doe gewenste output
#    cv2.imwrite(r'Projections\output.jpg', canvas)



if __name__ == '__main__':
    # bereken deze matrices 1 keer
    map_x, map_y = getTransformMatrices()

    times = []
    for i in range(50):
        start = time.perf_counter()
        perform_transform(map_x, map_y)     # deze functie kan zoveel uitgevoerd worden als gewenst, met zeer snelle execution (5ms voor 1440x1000)
        end = time.perf_counter()

        times.append(end-start)

    print(np.mean(times))