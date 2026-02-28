""" Network tables handling code """

import math
import time
import dataclasses

import numpy
from wpimath.geometry import Pose2d
import ntcore

from src import apriltag

@dataclasses.dataclass
class NetworkTable:
    """ Wrap network tables """

    def __init__(self, is_host: bool, team_number: int):

        nt_instance = ntcore.NetworkTableInstance.getDefault()

        # If this is hosting, start the server. Else, join the server
        if is_host:
            nt_instance.startServer()
        else:
            nt_instance.setServerTeam(team_number)
            nt_instance.startClient4("visionPi")


        self.table = nt_instance.getTable("AprilTag Vision")

        # Should be in NS
        self.fpga_offset = self.table.getIntegerTopic("FPGA Offset").subscribe(time.time_ns())

        # Returns whether we have a tag
        self.has_tag = self.table.getBooleanTopic("AprilTag Presence").publish()
        self.tag_count = self.table.getIntegerTopic("AprilTag Count").publish()

        # Global position of the robot
        # [x, y, theta]
        self.global_pose = self.table.getDoubleArrayTopic("Global Pose").publish()
        self.pose_timestamp = self.table.getDoubleTopic("Global Pose Timestamp").publish()

        # Which tag is "best" (most centered)
        self.best_tag_id = self.table.getIntegerTopic("Best Tag ID").publish()

        # Tag to camera transform (this is more useful than the raw pose)
        # [x, y, theta]
        self.tag_to_camera = self.table.getDoubleArrayTopic("Tag To Camera Pose").publish()

    def set_values(self, tags, robot_pose: Pose2d | None, best_tag: apriltag.Apriltag | None) -> None:
        """ Set important network tables values """
        self.has_tag.set(tags != [])
        self.tag_count.set(len(tags))

        # Publish global position & timestamp
        if robot_pose is not None:

            self.global_pose.set([robot_pose.x, robot_pose.y, robot_pose.rotation().radians()])
            self.pose_timestamp.set((time.time_ns() - self.fpga_offset.get()) / 1e9)

        if best_tag:
            # Publish local position & rotation

            # Calculate theta
            theta = best_tag.tag_to_camera.rotation().Z()
            theta -= numpy.sign(theta) * math.pi

            self.tag_to_camera.set([best_tag.tag_to_camera.X(), best_tag.tag_to_camera.Y(), theta])

            # Other
            self.best_tag_id.set(best_tag.id)
