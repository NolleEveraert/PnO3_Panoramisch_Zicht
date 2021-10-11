import cv2
import os

mainFolder = "alle fotos"  # folder waar python code in staat
mijnFolders = os.listdir(mainFolder)  # alle folders met fotos
print(mijnFolders)

schaal = 1  # hoe hard wordt de foto veranderd

for folder in mijnFolders:
    pad = mainFolder + "/" + folder
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
        cv2.imshow(f"Gestitchde foto: {folder}", result)
    else:
        print("Panorama gefaald")

cv2.waitKey()
