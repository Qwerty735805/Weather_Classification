import cv2

#Path of the image
file_path=''

picture = cv2.imread(file_path)

cv2.imwrite("test.png",picture)
