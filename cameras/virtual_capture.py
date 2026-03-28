""" Virtual camera capture to read from files """

import cv2
import numpy

from src.camera.capture import CaptureBase

class VirtualCapture(CaptureBase):
    """ Read images from files """
    current_file: str = ''

    def __init__(self):
        self.size: tuple[int, int] = (0, 0)

    def set_profile(self, profile: dict) -> None:
        self.size = (int(profile['resolution']['x']), int(profile['resolution']['y']))

    def get_frame(self) -> cv2.typing.MatLike:
        image = cv2.imread(VirtualCapture.current_file)

        if image is not None:
            h, w , _= image.shape
            if w == self.size[0] and h == self.size[1]:
                return image

        return numpy.zeros((self.size[0], self.size[1], 3), dtype=numpy.uint8)
