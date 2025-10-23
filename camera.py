""" Represent and initialize cameras """

import json
import dataclasses
import cv2
import numpy
from wpimath.geometry import Transform3d, Translation3d, Rotation3d, Quaternion
from cscore import CameraServer
import camera_calibration

def init_cameras(cameras):
    """ Initialize cameras """
    CameraServer.enableLogging()

    with open("config/CameraCalibration.json", 'r', encoding='utf-8') as file:
        profiles = json.load(file)

    max_width = 0
    max_height = 0

    for cam in cameras:
        if profiles[cam["profile"]]["resolution"]["x"] > max_width:
            max_width = profiles[cam["profile"]]["resolution"]["x"]
        if profiles[cam["profile"]]["resolution"]["y"] > max_height:
            max_height = profiles[cam["profile"]]["resolution"]["y"]

    output_stream = CameraServer.putVideo("Vision", max_width, max_height)

    # set camera settings (bash script)


    return output_stream

@dataclasses.dataclass
class Camera:
    """ Wrap cameras """

    def __init__(self, num, calibration):

        # Get values from JSON
        self.calibration = camera_calibration.CameraCalibration(calibration["profile"])
        offset = calibration["offset"]

        # Initialize actual camera portion
        self.cam = CameraServer.startAutomaticCapture(num)
        self.cam.setResolution(calibration.x_res, calibration.y_res)
        self.cv_sink = CameraServer.getVideo(self.cam)

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
        self.mat = numpy.zeros(shape=(calibration.x_res, calibration.y_res, 3), dtype=numpy.uint8)
        self.gray_mat = numpy.zeros(shape=(calibration.x_res, calibration.y_res), dtype=numpy.uint8)

        # Get correct rotation from calibration
        self.rotate_dist = calibration.rotation

    def update(self):
        """ Update images to latest """
        _, self.mat = self.cv_sink.grabFrame(self.mat)

        # Rotate image to be top-up
        if self.rotate_dist is not None:
            self.mat = cv2.rotate(self.mat, self.rotate_dist)

        self.gray_mat = cv2.cvtColor(self.mat, cv2.COLOR_RGB2GRAY)

        return self.mat, self.gray_mat

    def get_frame(self):
        """ Get frame from camera (lazily) """
        return self.mat
