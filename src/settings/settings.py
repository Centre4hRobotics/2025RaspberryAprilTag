""" Store the settings for the tags & stuff """

import dataclasses
import json

from robotpy_apriltag import AprilTagFieldLayout

from src import camera, network_tables, apriltag

from .filter import FilterList

@dataclasses.dataclass
class Settings:
    """ Store the settings generated in main.init() """

    def __init__(self, config: str, camera_type: camera.capture.CaptureBase):

        with open(config, encoding="utf-8") as file:
            settings_json = json.load(file)

        is_table_host: bool = settings_json["is table host"]
        team_number: int = settings_json["team number"]

        # Set the filter list
        self.filter_list = FilterList(settings_json)

        # Camera Stuff
        camera_profile = settings_json["camera"]["profile"]

        # Note: This may or may not work, I'm just guessing how cameras are assigned
        self.camera = camera.Camera(camera.CameraSettings.from_profile(camera_profile), camera_type)

        # Create the PoseEstimator & adjust its settings
        self.estimator = apriltag.apriltag_estimator.ApriltagEstimator(self.camera.calibration)

        # Creating the network tables
        self.tables = network_tables.NetworkTable(is_table_host, team_number)

        self.field = AprilTagFieldLayout(settings_json["field layout"])
