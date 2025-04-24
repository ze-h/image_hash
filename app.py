import cv2
import sys
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

if len(sys.argv) < 2:
    print("{} needs at least one argument".format(sys.argv[0]))
    print(
        "usage: {} <image for keygen> [optional]<file to encrypt> -(e,d)".format(
            sys.argv[0]
        )
    )
    exit(1)

# initialize the face recognizer (default face haar cascade)
# https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
face_cascade = cv2.CascadeClassifier(
    os.path.abspath("cascades/haarcascade_frontalface_default.xml")
)

# import image
image = cv2.imread(sys.argv[1])

# Detects faces of different sizes in the input image
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(gray, 1.3, 5)
(x, y, w, h) = faces[0]

# To draw a rectangle in a face
cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)
roi_gray = gray[y:y+h, x:x+w]
roi_color = image[y:y+h, x:x+w]
blur = cv2.blur(roi_gray, (10, 10))
_, thresholded = cv2.threshold(blur, 85, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# draw contours and save
cv2.drawContours(roi_color, contours, -1, (0, 255, 0), 2)
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

# check args
if len(sys.argv) == 3:
    print("encryption/decryption needs to be specified")
    print(
        "usage: {} <image for keygen> [optional]<file to encrypt> -(e,d)".format(
            sys.argv[0]
        )
    )
    exit(1)

if len(sys.argv) > 3:
    # check if file exists
    f = None
    try:
        f = open(sys.argv[2], "rb")
        pass
    except FileNotFoundError as e:
        print('"{}" not found.'.format(sys.argv[2]))
        print(
            "usage: {} <image for keygen> [optional]<file to encrypt> -(e,d)".format(
                sys.argv[0]
            )
        )
        exit(1)
    key = h.digest()
    cipher = Cipher(algorithms.AES256(key=key), modes.ECB())
    # encryption switch
    if sys.argv[3] in "-e-E":
        # encrypt file
        cyphertext = cipher.encryptor().update(f.read()) + cipher.encryptor().finalize()
        with open("output.hex", "wb") as out:
            out.write(cyphertext)
        f.close()
        exit(0)
    if sys.argv[3] in "-d-D":
        # decrypt file
        plaintext = cipher.decryptor().update(f.read()) + cipher.decryptor().finalize()
        with open("output.txt", "wb") as out:
            out.write(plaintext)
        f.close()
        exit(0)

    # neither, panic
    f.close()
    print("encryption/decryption needs to be specified")
    print(
        "usage: {} <image for keygen> [optional]<file to encrypt> -(e,d)".format(
            sys.argv[0]
        )
    )
    exit(1)
