import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from projection import *

IMG_LEFT_DICT = GANGLEFT_DICT
IMG_RIGHT_DICT = GANGRIGHT_DICT

HEIGHT, WIDTH = int(CANVAS_HEIGHT/2), int(CANVAS_WIDTH/2)


def render(event):
    global merged
    aperture_left_rad = aperture_left.get() * np.pi/180
    ar_left_rad = ar_left.get() * np.pi/180
    au_left_rad = au_left.get() * np.pi/180
    mapx_left, mapy_left = getTransformMatrices(aperture_left_rad, IMG_LEFT_DICT['center_x'], IMG_LEFT_DICT['center_y'], IMG_LEFT_DICT['radius'], ar_left_rad, au_left_rad)

    aperture_right_rad = aperture_right.get() * np.pi/180
    ar_right_rad = ar_right.get() * np.pi/180
    au_right_rad = au_right.get() * np.pi/180
    mapx_right, mapy_right = getTransformMatrices(aperture_right_rad, IMG_RIGHT_DICT['center_x'], IMG_RIGHT_DICT['center_y'], IMG_RIGHT_DICT['radius'], ar_right_rad, au_right_rad)
    
    result_left = perform_transform(IMG_LEFT_DICT['image'], mapx_left, mapy_left)
    result_right = perform_transform(IMG_RIGHT_DICT['image'], mapx_right, mapy_right)
    merged_1 = cv2.resize(merge(result_left, result_right), dsize=(WIDTH, HEIGHT))      # merge and resize
    merged_2 = cv2.cvtColor(merged_1.astype(np.uint8), cv2.COLOR_BGR2RGB)               # convert to np.uint8 and to RGB
    merged = ImageTk.PhotoImage(Image.fromarray(merged_2))                              # convert to PIL Image and subsequently to PhotoImage

    canvas.itemconfig(image_sprite, image=merged)



window = tk.Tk()

aperture_left = tk.Scale(window, from_=180, to=210, command=render)
aperture_left.set(0)
aperture_left.pack(side=tk.LEFT)
ar_left = tk.Scale(window, from_=-10, to=10, command=render)
ar_left.set(0)
ar_left.pack(side=tk.LEFT)
au_left = tk.Scale(window, from_=-10, to=10, command=render)
au_left.set(0)
au_left.pack(side=tk.LEFT)

canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT)
merged = ImageTk.PhotoImage(Image.fromarray(np.full((HEIGHT, WIDTH, 3), 100, dtype=np.uint8)))
image_sprite = canvas.create_image(0,0, image=merged, anchor="nw")
canvas.pack(side=tk.LEFT)

aperture_right = tk.Scale(window, from_=180, to=210, command=render)
aperture_right.set(200)
aperture_right.pack(side=tk.LEFT)
ar_right = tk.Scale(window, from_=-10, to=10, command=render)
ar_right.set(0)
ar_right.pack(side=tk.LEFT)
au_right = tk.Scale(window, from_=-10, to=10, command=render)
au_right.set(0)
au_right.pack(side=tk.LEFT)



window.mainloop()
