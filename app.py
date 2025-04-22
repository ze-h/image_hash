import cv2
import sys
import rembg
import hashlib

if len(sys.argv) < 2:
    print("{} needs at least one argument".format(sys.argv[0]))
    exit(1)

# import image and remove bg
imagebg = cv2.imread(sys.argv[1])
cv2.imwrite("nobg.jpg", rembg.remove(imagebg))
image = cv2.imread("nobg.jpg")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)

_, thresholded = cv2.threshold(blur, 85, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# draw contours and save
cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
cv2.imwrite("contours.jpg", image)

# take sum of point products
contourtxt = 0
for contour in contours:
    for line in contour:
        for point in line:
            contourtxt += point[0] * point[1]

# hash to 256, save
h = hashlib.sha256()
h.update(bytes(str(contourtxt).encode()))
with open("contours.hex", "wb") as file:
    file.write(h.digest())
