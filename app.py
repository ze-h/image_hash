import cv2
import sys
import rembg
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

if len(sys.argv) < 2:
    print("{} needs at least one argument".format(sys.argv[0]))
    print(
        "usage: {} <image for keygen> [optional]<file to encrypt> -(e,d)".format(
            sys.argv[0]
        )
    )
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
