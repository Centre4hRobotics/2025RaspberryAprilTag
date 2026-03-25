""" Use OpenCV to capture images """

import cv2

from src.camera.capture import CaptureBase

class OpenCVCapture(CaptureBase):
    """ Define a base class for camera captures """

    def __init__(self, camera_index: int) -> None:
        self.capture = cv2.VideoCapture(camera_index)

        if not self.capture.isOpened():
            raise RuntimeError("Failed to open camera!")

    def set_profile(self, profile: dict) -> None:
        """ Set camera profile """
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, profile['resolution']['x'])
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, profile['resolution']['y'])

    def get_frame(self) -> cv2.typing.MatLike:
        """ Get frame from camera """

        ret, frame = self.capture.read()

        if ret:
            return frame
        else:
            raise RuntimeError("Failed to get frame from camera!")
