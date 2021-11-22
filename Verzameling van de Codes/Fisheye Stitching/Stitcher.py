import cv2
import os

video_name = 'video.mp4'

frame = cv2.imread('Ja.png')
height, width, layers = frame.shape

video = cv2.VideoWriter(video_name, 0, 1, (width,height))

for i in range(1000):
    video.write(frame)

cv2.destroyAllWindows()
video.release()