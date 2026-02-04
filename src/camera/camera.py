""" Represent and initialize cameras """

import json
import dataclasses

import cv2
import numpy
import picamera2
from wpimath.geometry import Transform3d, Translation3d, Rotation3d, Quaternion
from cscore import CameraServer

from src.camera import calibration


@dataclasses.dataclass
class Camera:
    """ Wrap cameras """

    def __init__(self, _calibration: dict) -> None:
        CameraServer.enableLogging()

        with open("config/CameraProfiles.json", 'r', encoding='utf-8') as file:
            profiles = json.load(file)

        profile = profiles[_calibration['profile']]["resolution"]

        self.output_stream = CameraServer.putVideo("Vision", profile['x'], profile['y'])

        # Get values from JSON
        self.calibration = calibration.CameraCalibration(_calibration["profile"])
        offset = _calibration["offset"]

        # Initialize actual camera portion
        self.cam = picamera2.Picamera2()

        camera_config = self.cam.create_video_configuration(
            main={
                'size': (profile['x'], profile['y'])
            }
        )

        self.cam.configure(camera_config)
        self.cam.start()

        # Get the offset from JSON
        self.offset = Transform3d(
            Translation3d(
                offset["position"][0],
                offset["position"][1],
                offset["position"][2]
            ),
            Rotation3d(
                Quaternion(
                    offset["rotation"][0],
                    offset["rotation"][1],
                    offset["rotation"][2],
                    offset["rotation"][3]
                )
            )
        )

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

        self.mat = self.cam.capture_array()

        # Rotate image to be top-up
        if self.rotate_dist is not None:
            self.mat = cv2.rotate(self.mat, self.rotate_dist)

        self.gray_mat = cv2.cvtColor(self.mat, cv2.COLOR_RGB2GRAY)

    def get_frame(self):
        """ Get frame from camera (lazily) """
        return self.gray_mat
