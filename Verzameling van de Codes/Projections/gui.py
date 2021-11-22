import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from projection import *

IMG_LEFT_DICT = GANGLEFT_DICT
IMG_RIGHT_DICT = GANGRIGHT_DICT


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
    merged_rgb = cv2.cvtColor(merge(result_left, result_right).astype(np.uint8), cv2.COLOR_BGR2RGB)
    merged1 = Image.fromarray(merged_rgb)
    merged = ImageTk.PhotoImage(merged1)

    canvas.itemconfig(image_sprite, image=merged)



window = tk.Tk()

aperture_left = tk.Scale(window, from_=180, to=210, command=render)
aperture_left.set(0)
aperture_left.pack()
ar_left = tk.Scale(window, from_=-10, to=10, command=render)
ar_left.set(0)
ar_left.pack()
au_left = tk.Scale(window, from_=-10, to=10, command=render)
au_left.set(0)
au_left.pack()

canvas = tk.Canvas(window, width=CANVAS_WIDTH+5, height=CANVAS_HEIGHT+5)
merged = ImageTk.PhotoImage(Image.fromarray(np.full((CANVAS_HEIGHT, CANVAS_WIDTH, 3), 100, dtype=np.uint8)))
image_sprite = canvas.create_image(0,0, image=merged, anchor="nw")
canvas.pack()

aperture_right = tk.Scale(window, from_=180, to=210, command=render)
aperture_right.set(200)
aperture_right.pack()
ar_right = tk.Scale(window, from_=-10, to=10, command=render)
ar_right.set(0)
ar_right.pack()
au_right = tk.Scale(window, from_=-10, to=10, command=render)
au_right.set(0)
au_right.pack()



window.mainloop()
