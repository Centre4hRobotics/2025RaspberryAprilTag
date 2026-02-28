""" Represent and initialize cameras """

import json
import dataclasses

import cv2
import numpy
import picamera2
from wpimath.geometry import Transform3d, Translation3d, Rotation3d, Quaternion
from cscore import CameraServer

from src.camera import calibration, camera_capture

@dataclasses.dataclass
class Camera:
    """ Wrap cameras """

    def __init__(self, camera_settings: dict, capture: camera_capture.CaptureBase) -> None:
        CameraServer.enableLogging()

        with open('config/CameraProfiles.json', 'r', encoding='utf-8') as file:
            profiles = json.load(file)

        profile = profiles[camera_settings['profile']]['resolution']

        self.output_stream = CameraServer.putVideo('Vision', profile['x'], profile['y'])

        self.capture = capture
        self.capture.set_profile(profile)

        # Get values from JSON
        self.calibration = calibration.CameraCalibration(camera_settings['profile'])

        # Initialize image
        self.mat = numpy.zeros(
            shape=(self.calibration.x_res, self.calibration.y_res, 3),
            dtype=numpy.uint8
        )
        self.gray_mat = numpy.zeros(
            shape=(self.calibration.x_res, self.calibration.y_res),
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
