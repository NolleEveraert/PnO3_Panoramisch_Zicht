# Tutorial: https://www.youtube.com/watch?v=8oFRmdDum5k

import cv2

schaal = 1.2

fotos = []
foto1 = cv2.imread("../IS met folders/alle fotos/fotos Thuis/Thuis 1.jpg")
foto1 = cv2.resize(foto1, (0, 0), None, schaal, schaal)
foto2 = cv2.imread("../IS met folders/alle fotos/fotos Thuis/Thuis 2.jpg")
foto2 = cv2.resize(foto2, (0, 0), None, schaal, schaal)

fotos.append(foto1)
fotos.append(foto2)

stitcher = cv2.Stitcher.create()
status, result = stitcher.stitch(fotos)

if status == cv2.STITCHER_OK:
    print("Panorama gemaakt")
    cv2.imshow("Code eerste test IS", result)
    cv2.waitKey(1)
else:
    print("Panorama gefaald")

cv2.waitKey(0)
