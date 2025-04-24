import cv2
import os

# initialize the face recognizer (default face haar cascade)
# https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
face_cascade = cv2.CascadeClassifier(os.path.abspath("cascades/haarcascade_frontalface_default.xml"))

# eye recognizer
# https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_eye.xml
eye_cascade = cv2.CascadeClassifier(os.path.abspath("cascades/haarcascade_eye.xml"))

# Open the default camera
cam = cv2.VideoCapture(0)
orb = cv2.ORB_create()

# Get the default frame width and height
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

while True:
    ret, frame = cam.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detects faces of different sizes in the input image
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:
        # To draw a rectangle in a face 
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,255,0),2) 
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]

        # Detects eyes of different sizes in the input image
        eyes = eye_cascade.detectMultiScale(roi_gray) 

        #To draw a rectangle in eyes
        for (ex,ey,ew,eh) in eyes:
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,127,255),2)

        blur = cv2.blur(roi_gray, (10, 10))

        _, thresholded = cv2.threshold(blur, 85, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # draw contours and save
        cv2.drawContours(roi_color, contours, -1, (0, 255, 0), 2)

        # get number
        # take sum of point products
        contourtxt = 0
        for contour in contours:
            for line in contour:
                for point in line:
                    contourtxt += point[0] * point[1]

        
        #keypoints, descriptors = orb.detectAndCompute(blur, None)
        #new_color = cv2.drawKeypoints(roi_color, keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        # add text
        text = f"C = {contourtxt}"
        coordinates = (x,y)
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        color = (0,0,255)
        thickness = 3
        cv2.putText(frame, text, coordinates, font, fontScale, color, thickness, cv2.LINE_AA)

        # Display the captured frame
        cv2.imshow('xxx', blur)

    # Display the captured frame
    cv2.imshow('Camera', frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break

# Release the capture and writer objects
cam.release()
cv2.destroyAllWindows()