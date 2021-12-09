import numpy as np
import cv2
import time
import os


img_dir = r'Verzameling van de Codes\Projections'


# img = cv2.imread(r'Verzameling van de Codes\Projections\fisheye-210.jpg')
# FISHEYE_DICT = {
#     'image': img,
#     'aperture_rad': 210 * np.pi/180,
#     'img_height': img.shape[:2][0],
#     'img_width': img.shape[:2][1],
#     'radius': 1024,
#     'center_x': 1024,
#     'center_y': 1024+96,
#     'output_path': r'Verzameling van de Codes\Projections\fisheye-output.jpg',
# }

img = cv2.imread(os.path.join(img_dir, 'comp-left.jpg'))
COMPLEFT_DICT = {
    'name': "comp-left",
    'image': img,
    'aperture_rad': 200 * np.pi/180,
    'img_height': img.shape[:2][0],     #2592
    'img_width': img.shape[:2][1],      #1920
    'radius': 1070,       # mistakes in radius do not matter, as long as radius/aperture is right
    'center_x': 1150,
    'center_y': 970,
    'output_path': os.path.join(img_dir, 'comp-left-output.jpg'),
}

img = cv2.imread(os.path.join(img_dir, 'comp-right.jpg'))
COMPRIGHT_DICT = {
    'name': "comp-right",
    'image': img,
    'aperture_rad': 200 * np.pi/180,
    'img_height': img.shape[:2][0],
    'img_width': img.shape[:2][1],
    'radius': 1070,     #1078
    'center_x': 1256,
    'center_y': 970,
    'output_path': os.path.join(img_dir, 'comp-right-output.jpg'),
}

img = cv2.imread(os.path.join(img_dir, 'gang_left.jpg'))
GANGLEFT_DICT = {
    'name': "gang-left",
    'image': img,
    'aperture_rad': 200 * np.pi/180,
    'img_height': img.shape[:2][0],
    'img_width': img.shape[:2][1],
    'radius': 1070,     #1078
    'center_x': 1160,
    'center_y': 957,
    'a_up': 0,
    'a_right': 0,
    'output_path': os.path.join(img_dir, 'gang-left-output.jpg'),
}

img = cv2.imread(os.path.join(img_dir, 'gang_right.jpg'))
GANGRIGHT_DICT = {
    'name': "gang-right",
    'image': img,
    'aperture_rad': 200 * np.pi/180,
    'img_height': img.shape[:2][0],
    'img_width': img.shape[:2][1],
    'radius': 1070,     #1078
    'center_x': 1257,
    'center_y': 940,
    'a_up': 0,
    'a_right': 0,
    'output_path': os.path.join(img_dir, 'gang-right-output.jpg'),
}

img = cv2.imread(os.path.join(img_dir, '49_left.png'))
LEFT49_DICT = {
    'name': "left49",
    'image': img,
    'aperture_rad': 200 * np.pi/180,
    'img_height': img.shape[:2][0],
    'img_width': img.shape[:2][1],
    'radius': 1070/2592 * img.shape[:2][1],     #330
    'center_x': 1160/2592 * img.shape[:2][1],   #358
    'center_y': 957/1920 * img.shape[:2][0],    #303
    'a_up': 0,
    'a_right': 0,
}

img = cv2.imread(os.path.join(img_dir, '49_right.jpg'))
RIGHT49_DICT = {
    'name': "right49",
    'image': img,
    'aperture_rad': 200 * np.pi/180,
    'img_height': img.shape[:2][0],
    'img_width': img.shape[:2][1],
    'radius': 1070/2592 * img.shape[:2][1],     #330
    'center_x': 1257/2592 * img.shape[:2][1],   #388
    'center_y': 940/1920 * img.shape[:2][0],    #298
    'a_up': 0,
    'a_right': 0,
}



CANVAS_WIDTH = 1440
CANVAS_HEIGHT = 1000
MARGIN = 0.03       # het percentage van de breedte dat als marge wordt genomen
#0.015


"""
Berekent matrices map_x en map_y die specifieren voor elke pixel in de output image, waar die pixel vandaan komt in de input image (fisheye).
Deze moeten 1 keer berekend worden, en blijven daarna voor de rest van de executie hetzelfde.
"""
def getTransformMatrices(aperture_rad, center_x, center_y, radius, a_right=0, a_up=0):
    # de oorspronkelijke coordinaten van elke pixel
    # Xe[y,x] = x; Ye[y,x] = y
    Xe = np.tile(np.arange(CANVAS_WIDTH, dtype=np.float32), (CANVAS_HEIGHT,1))
    Ye = np.tile(np.arange(CANVAS_HEIGHT, dtype=np.float32).reshape((CANVAS_HEIGHT, 1)), (1,CANVAS_WIDTH))

    # x_norm and y_norm in [-1,1]
    x_norm = Xe * 2/CANVAS_WIDTH - 1
    y_norm = Ye * 2/CANVAS_HEIGHT - 1

    # lengtegraad en breedtegraad van elke pixel
    long = x_norm * np.pi + a_right
    lat = y_norm * np.pi/2 + a_up

    # 3D coordinaten van elke pixel (op een boloppervlak)
    Px = np.cos(lat) * np.cos(long)
    Py = np.cos(lat) * np.sin(long)
    Pz = np.sin(lat)

    # polaire coordinaten op de fisheye image
    r = 2 * np.arctan2(np.sqrt(Px*Px + Pz*Pz), Py) / aperture_rad
    theta = np.arctan2(Pz, Px)

    # reele cartesische coordinaten op de fisheye image
    map_x = center_x + r*radius*np.cos(theta)
    map_y = center_y + r*radius*np.sin(theta)

    return map_x, map_y


def perform_transform(img, map_x, map_y):

    canvas = cv2.remap(img, map_x, map_y, interpolation=cv2.INTER_LINEAR)

    # doe gewenste output
    return canvas


def center(img):
    return np.hstack((img[:, int((1/2-MARGIN)*CANVAS_WIDTH) : CANVAS_WIDTH], img[:, : int(MARGIN * CANVAS_WIDTH)]))

def getMargins(img):
    return img[:, int((1/2-MARGIN)*CANVAS_WIDTH) : int((1/2+MARGIN)*CANVAS_WIDTH)], \
        np.hstack((img[:, int((1-MARGIN)*CANVAS_WIDTH) : CANVAS_WIDTH], img[:, : int(MARGIN * CANVAS_WIDTH)]))

def norm_correlation(a, b):
    # the higher, the better
    assert a.shape == b.shape
    if not a.dtype == b.dtype == np.uint8:
        print("WARNING: one array does not have type np.uint8")
    
    c = a.astype(np.uint64)
    d = b.astype(np.uint64)
    return np.sum(c*d) / (np.sqrt(np.sum(c*c)) * np.sqrt(np.sum(d*d)))


def compare(img_dict1, img_dict2, ap1, ap2) -> int:
    ap1_rad = ap1 * np.pi/180
    ap2_rad = ap2 * np.pi/180

    map_x, map_y = getTransformMatrices(ap1_rad, img_dict1['center_x'], img_dict1['center_y'], img_dict1['radius'])
    result1 = perform_transform(img_dict1['image'], map_x, map_y)
    map_x, map_y = getTransformMatrices(ap2_rad, img_dict2['center_x'], img_dict2['center_y'], img_dict2['radius'])
    result2 = perform_transform(img_dict2['image'], map_x, map_y)

    # cv2.imwrite("Verzameling van de Codes\Projections\\debug\\" + img_dict1['name'] + f"_resultbefore_{ap1}.jpg", result1)

    margins1 = getMargins(result1)
    margins2 = getMargins(result2)[::-1]
    # cv2.imwrite("Verzameling van de Codes\Projections\\debug\\" + img_dict1['name'] + f"_result_{ap1}.jpg", result1)
    # cv2.imwrite("Verzameling van de Codes\Projections\\debug\\" + img_dict1['name'] + f"_margin0_{ap1}.jpg", margins1[0])
    # cv2.imwrite("Verzameling van de Codes\Projections\\debug\\" + img_dict1['name'] + f"_margin1_{ap1}.jpg", margins1[1])

    metric0 = round(norm_correlation(margins1[0], margins2[0]), 2)
    metric1 = round(norm_correlation(margins1[1], margins2[1]), 2)
    metric = round(metric0 + metric1, 2)

    debug_img = np.hstack((margins1[0], np.zeros((CANVAS_HEIGHT, 10, 3)), margins2[0], \
            np.zeros((CANVAS_HEIGHT, 50, 3)), \
            margins1[1], np.zeros((CANVAS_HEIGHT, 10, 3)), margins2[1]
    ))
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(debug_img, str(metric0), (0,30), font, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.putText(debug_img, str(metric1), (int(debug_img.shape[1]/2), 30), font, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
    
    cv2.imwrite("Verzameling van de Codes\Projections\\debug\\" + img_dict1['name'] + "_" + img_dict2['name'] + f"___{ap1}-{ap2}.png", \
        debug_img)

    merged = merge(result1, result2)
    cv2.putText(merged, str(metric1), (int(CANVAS_WIDTH/2)-50, 30), font, 0.5, (0,255,0), 2, cv2.LINE_AA)
    cv2.putText(merged, str(metric0), (int(CANVAS_WIDTH)-50, 30), font, 0.5, (0,255,0), 2, cv2.LINE_AA)
    cv2.imwrite("Verzameling van de Codes\Projections\\results\\" + img_dict1['name'] + "_" + img_dict2['name'] + f"___{ap1}-{ap2}.png", \
        merged)

    return metric


def merge(left, right):
    lmargins = getMargins(left)
    rmargins = getMargins(right)[::-1]
    
    assert lmargins[0].shape[1] == rmargins[0].shape[1]
    assert lmargins[1].shape[1] == rmargins[1].shape[1]
    
    margin_width = lmargins[0].shape[1]
    linspace_colvec = np.expand_dims(np.linspace(0, 1, num=margin_width), axis=0).transpose()
    right_interpolation = np.tile(linspace_colvec, (1,3))
    left_interpolation = 1 - right_interpolation
    margin0_interpolated = lmargins[0] * right_interpolation + rmargins[0] * left_interpolation
    margin1_interpolated = lmargins[1] * left_interpolation + rmargins[1] * right_interpolation

    result = np.hstack((
        left[:, int((1/2+MARGIN)*CANVAS_WIDTH) : int((1-MARGIN)*CANVAS_WIDTH)],
        margin1_interpolated,
        right[:, int((1/2+MARGIN)*CANVAS_WIDTH) : int((1-MARGIN)*CANVAS_WIDTH)],
        margin0_interpolated,
    ))
    #return np.roll(result, shift=int(margin_width/2), axis=1)
    return result       # rollen neemt veel tijd en is niet nodig
    

def main():
    for aperture in range(180, 202, 2):
        aperture_rad = aperture * np.pi/180
        for img_dict in [GANGLEFT_DICT, GANGRIGHT_DICT]:
            map_x, map_y = getTransformMatrices(aperture_rad, img_dict['center_x'], img_dict['center_y'], img_dict['radius'])
            result = perform_transform(img_dict['image'], map_x, map_y)

            #output per result
            output_path = "Verzameling van de Codes\Projections\\tests\\gang\\" + img_dict['name'] + str(aperture) + '.jpg'
            cv2.imwrite(output_path, center(result))


def compare_main():
    for ap1 in np.arange(182, 210, 2):
        for ap2 in range(182, 210, 2):
            metric = compare(GANGLEFT_DICT, GANGRIGHT_DICT, ap1, ap2)
            print(f"(ap1, ap2) = ({ap1}, {ap2}): ".ljust(40) + str(metric))


if __name__ == '__main__':
    compare_main()