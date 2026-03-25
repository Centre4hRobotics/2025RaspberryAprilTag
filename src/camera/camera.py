""" Represent and initialize cameras """

import dataclasses

import cv2
import numpy
from cscore import CameraServer

from . import capture, settings

@dataclasses.dataclass
class Camera:
    """ Wrap cameras """

    def __init__(self, camera_settings: settings.CameraSettings, capture_: capture.CaptureBase) -> None:
        CameraServer.enableLogging()

        self.calibration = camera_settings.calibration

        self.output_stream = CameraServer.putVideo('Vision', camera_settings.x_res, camera_settings.y_res)

        self.capture = capture_
        self.capture.set_profile(camera_settings.profile)

        # Get values from JSON


        # Initialize image
        self.mat = numpy.zeros(
            shape=(camera_settings.x_res, camera_settings.y_res, 3),
            dtype=numpy.uint8
        )
        self.gray_mat = numpy.zeros(
            shape=(camera_settings.x_res, camera_settings.y_res),
            dtype=numpy.uint8
        )

        # Get correct rotation from calibration
        self.rotate_dist = self.calibration.rotation

    def update(self):
        """ Update images to latest """

        self.mat = self.capture.get_frame()

        self.gray_mat = cv2.cvtColor(self.mat, cv2.COLOR_RGB2GRAY)

    def get_frame(self):
        """ Get frame from camera """
        return self.gray_mat

    def rotate_mat(self):
        """ Rotate mat to be top-up (**MUST** be done **AFTER** all processing!!) """
        if self.rotate_dist is not None:
            self.mat = cv2.rotate(self.mat, self.rotate_dist)
