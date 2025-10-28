""" Represent cameras! """

import json
import dataclasses
import numpy
import cv2

@dataclasses.dataclass
class CameraCalibration:
    # I see the pylint warning, but these are all so closely related that they should still be here.
    """ Store camera calibration data """
    def __init__(self, profile):
        with open('config/CameraCalibration.json', encoding="utf-8") as file:
            calibration_data = json.load(file)

        camera_data = calibration_data[profile]

        fx = camera_data["intrinsics"]["Fx"]
        fy = camera_data["intrinsics"]["Fy"]
        cx = camera_data["intrinsics"]["Cx"]
        cy = camera_data["intrinsics"]["Cy"]

        self.x_res = camera_data["resolution"]["x"]
        self.y_res = camera_data["resolution"]["y"]

        self.camera_distortion = numpy.float32([
            camera_data["distortion"]["A"],
            camera_data["distortion"]["B"],
            camera_data["distortion"]["C"],
            camera_data["distortion"]["D"],
            camera_data["distortion"]["E"]
        ]) # pyright: ignore[reportArgumentType]
        self.camera_intrinsics = numpy.eye(3)
        self.camera_intrinsics[0][0] = fx
        self.camera_intrinsics[1][1] = fy
        self.camera_intrinsics[0][2] = cx
        self.camera_intrinsics[1][2] = cy

        match calibration_data["rotation"]:
            case "90":
                self.rotation = cv2.ROTATE_90_CLOCKWISE
            case "180":
                self.rotation = cv2.ROTATE_180
            case "270":
                self.rotation = cv2.ROTATE_90_COUNTERCLOCKWISE
            case "-90":
                self.rotation = cv2.ROTATE_90_COUNTERCLOCKWISE
            case "0":
                self.rotation = None
