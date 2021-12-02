from projection import getTransformMatrices, perform_transform, merge, GANGLEFT_DICT, GANGRIGHT_DICT
import time

mapx_left, mapy_left = getTransformMatrices(GANGLEFT_DICT['aperture_rad'], GANGLEFT_DICT['center_x'], GANGLEFT_DICT['center_y'], GANGLEFT_DICT['radius'])
mapx_right, mapy_right = getTransformMatrices(GANGRIGHT_DICT['aperture_rad'], GANGRIGHT_DICT['center_x'], GANGRIGHT_DICT['center_y'], GANGRIGHT_DICT['radius'])

start = time.perf_counter()
for i in range(100):
    left_result = perform_transform(GANGLEFT_DICT['image'], mapx_left, mapy_left)
    right_result = perform_transform(GANGRIGHT_DICT['image'], mapx_right, mapy_right)
end = time.perf_counter()
print('\n---projections---')
print('time:', end-start)
print('fps:', 100/(end-start))


start = time.perf_counter()
for i in range(100):
    result = merge(left_result, right_result)
end = time.perf_counter()
print('\n---merge---')
print('time:', end-start)
print('fps:', 100/(end-start))