import cv2
from numpy import ndarray

camera: cv2.VideoCapture | None = None


def get_camera(camera_port: int = 0) -> bool:
    """
    This function initializes the camera

    :param camera_port: The camera port
    :return: True if the camera was initialized successfully, False otherwise
    """
    global camera
    camera = cv2.VideoCapture(camera_port)
    if camera is None or not camera.isOpened():
        camera = None
        return False
    camera.set(3, 1280)
    camera.set(4, 960)
    return True


def release_camera() -> None:
    """
    This function releases the camera
    """
    global camera
    camera.release()
    camera = None


def get_camera_image() -> ndarray | None:
    """
    This function captures an image from the camera
    :return: A PIL Image object if the image was captured successfully, None otherwise
    """
    result, image = camera.read()
    if not result:
        return None
    result, image_encoded = cv2.imencode(".jpg", image)
    return image_encoded if result else None
