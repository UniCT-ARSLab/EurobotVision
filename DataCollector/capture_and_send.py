# program to capture single image from webcam in python

# importing OpenCV library
import cv2
import gdrive
import datetime


# initialize the camera
# If you have multiple camera connected with
# current device, assign a value in cam_port
# variable according to that
def capture_image_and_send():
    ts = datetime.datetime.now().timestamp()
    cam_port = 1
    cam = cv2.VideoCapture(cam_port)
    cam.set(3, 1920)
    cam.set(4, 1080)

    # reading the input using the camera
    result, image = cam.read()
    name = str(ts) + ".jpg"

    # If image will detected without any error,
    # show result
    if result:
        # showing result, it take frame name and image
        _, buffer = cv2.imencode(".jpg", image)

    # If captured image is corrupted, moving to else part
    else:
        print("No image detected.")

    gdrive.upload_photo(name, buffer)
