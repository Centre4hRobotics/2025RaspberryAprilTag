""" Store the settings for the tags & stuff """

import dataclasses
import json

from robotpy_apriltag import AprilTagFieldLayout

from src import camera, network_tables, apriltag

from .filter import FilterList

@dataclasses.dataclass
class Settings:
    """ Store the settings generated in main.init() """

    def __init__(self, config: str, camera_types: list[camera.camera_capture.CaptureBase]):

        with open(config, encoding="utf-8") as file:
            settings_json = json.load(file)

        is_table_host: bool = settings_json["is table host"]
        team_number: int = settings_json["team number"]

        # Set the filter list
        self.filter_list = FilterList(settings_json)

        # Camera Stuff
        camera_data = settings_json["camera"]

        # Note: This may or may not work, I'm just guessing how cameras are assigned
        self.cameras = [camera.Camera(camera_data, camera_type) for camera_type in camera_types]

        # Create the PoseEstimator & adjust its settings
        self.estimators = [apriltag.apriltag_estimator.ApriltagEstimator(camera.calibration) for camera in self.cameras]

        # Creating the network tables
        self.tables = network_tables.NetworkTable(is_table_host, team_number)

        self.field = AprilTagFieldLayout(settings_json["field layout"])
