import cv2


def get_camera_image(camera_port: int = 0) -> cv2.typing.MatLike | None:
    """
    This function captures an image from the camera
    :return: The image as bytes if successful, None otherwise
    """
    cam = cv2.VideoCapture(camera_port)
    cam.set(3, 1280)
    cam.set(4, 960)
    result, image = cam.read()
    cam.release()
    return image if result else None
