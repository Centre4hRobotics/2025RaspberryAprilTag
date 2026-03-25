""" Define settings for cameras """

import dataclasses
import json

from . import calibration

@dataclasses.dataclass
class CameraSettings:
    """ Define settings for cameras"""

    def __init__(self, settings: dict):
        self.profile = settings

        self.calibration = calibration.CameraCalibration(settings)

        self.x_res = settings['resolution']['x']
        self.y_res = settings['resolution']['y']


    @classmethod
    def from_profile(cls, profile: str):
        """ Create CameraSettings object from dict (json) """


        with open('config/CameraProfiles.json', 'r', encoding='utf-8') as file:
            profiles = json.load(file)

        return cls(profiles[profile])
