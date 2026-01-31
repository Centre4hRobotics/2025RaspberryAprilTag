""" Store the settings for the tags & stuff """

import dataclasses
from enum import Enum
import json

from src.apriltag import apriltag_estimator
from src.camera import camera
from src import network_tables

class ListType(Enum):
    """ Determine which type of List (blacklist or whitelist) is being used. """
    WHITELIST = 0
    BLACKLIST = 1

@dataclasses.dataclass
class FilterList:
    """ Keep blacklist/whitelist in one place """

    def __init__(self, config):

        if config["whitelist"] is not None and config["blacklist"] is not None:
            raise ValueError("Whitelist and Blacklist are both set!")

        if config["blacklist"] is not None:
            self.list = config["blacklist"]
            self.type = ListType.BLACKLIST

        elif config["whitelist"] is not None:
            self.list = config["whitelist"]
            self.type = ListType.WHITELIST

        else: # No blacklist or whitelist; allow all tags
            self.list = []
            self.type = ListType.BLACKLIST

    def filter_tags(self, tags):
        """ Remove filtered entries from a list. """

        if self.type is ListType.WHITELIST:
            return [tag for tag in tags if tag.id in self.list] # remove elements not in whitelist

        return [tag for tag in tags if tag.id not in self.list] # remove elements in blacklist

@dataclasses.dataclass
class Settings:
    """ Store the settings generated in main.init() """

    def __init__(self, config):

        with open(config, encoding="utf-8") as file:
            settings_json = json.load(file)

        is_table_host: bool = settings_json["is table host"]
        team_number: int = settings_json["team number"]

        # Set the filter list
        self.filter_list = FilterList(settings_json)

        # Camera Stuff
        camera_data = settings_json["cameras"]

        self.output_stream = camera.init_cameras(camera_data)

        # Note: This may or may not work, I'm just guessing how cameras are assigned
        self.cameras = [camera.Camera(2 * i, c) for i, c in enumerate(camera_data)]

        # Create the PoseEstimator & adjust its settings
        self.estimators = [
            apriltag_estimator.ApriltagEstimator(cam.calibration)
            for cam in self.cameras
        ]

        # Creating the network tables
        self.tables = network_tables.NetworkTable(is_table_host, team_number)
