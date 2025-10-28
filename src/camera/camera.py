""" Represent and initialize cameras """

import subprocess
import json
import dataclasses
import cv2
import numpy
from wpimath.geometry import Transform3d, Translation3d, Rotation3d, Quaternion
from cscore import CameraServer
import calibration

def init_cameras(cameras):
    """ Initialize cameras """
    CameraServer.enableLogging()

    with open("config/CameraCalibration.json", 'r', encoding='utf-8') as file:
        profiles = json.load(file)

    used_profiles = [profiles[c]["resolution"] for c in cameras]

    max_width = max(p["x"] for p in used_profiles)
    max_height = max(p["y"] for p in used_profiles)

    output_stream = CameraServer.putVideo("Vision", max_width, max_height)

    # set camera settings (bash script)


    return output_stream

@dataclasses.dataclass
class Camera:
    """ Wrap cameras """

    def __init__(self, num: int, cal: dict) -> None:

        # Get values from JSON
        self.calibration = calibration.CameraCalibration(cal["profile"])
        offset = cal["offset"]

        # Initialize actual camera portion
        self.cam = CameraServer.startAutomaticCapture(num)
        self.cam.setResolution(self.calibration.x_res, self.calibration.y_res)
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
        self.mat = numpy.zeros(shape=(self.calibration.x_res, self.calibration.y_res, 3), dtype=numpy.uint8)
        self.gray_mat = numpy.zeros(shape=(self.calibration.x_res, self.calibration.y_res), dtype=numpy.uint8)

        # Get correct rotation from calibration
        self.rotate_dist = self.calibration.rotation

        # Set camera settings (bash script)
        try:
            script = "/home/pi/2025RaspberryAprilTag/config/set_camera_settings.sh"
            result = subprocess.run(
                f"sh {script}", # Runs the script
                capture_output=True,
                text=True,
                check=True # Raises an error if this fails
            )
            print(result)
        except subprocess.CalledProcessError as err:
            print(f"Error running {err}")
            print(f"Error: {err.stderr}")

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
