""" Represent cameras! """

import json
import numpy

class CameraCalibration:
    def __init__(self, profile):
        with open('config/CameraCalibration.json', encoding="utf-8") as file:
            calibration_data = json.load(file)

        camera_data = calibration_data[profile]
        
        self.fx = camera_data["Intrinsics"]["Fx"]
        self.fy = camera_data["Intrinsics"]["Fy"]
        self.cx = camera_data["Intrinsics"]["Cx"]
        self.cy = camera_data["Intrinsics"]["Cy"]

        self.x_res = camera_data["Resolution"]["x"]
        self.y_res = camera_data["Resolution"]["y"]

        self.camera_distortion = numpy.float32([
            camera_data["Distortion"]["A"],
            camera_data["Distortion"]["B"],
            camera_data["Distortion"]["C"],
            camera_data["Distortion"]["D"],
            camera_data["Distortion"]["E"] ])
        self.camera_intrinsics = numpy.eye(3)
        self.camera_intrinsics[0][0] = self.fx
        self.camera_intrinsics[1][1] = self.fy
        self.camera_intrinsics[0][2] = self.cx
        self.camera_intrinsics[1][2] = self.cy
