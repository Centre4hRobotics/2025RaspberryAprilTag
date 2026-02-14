""" Network tables handling code """

import math
import time
import dataclasses

import numpy
from wpimath.geometry import Pose2d
import ntcore

from src.apriltag import apriltag

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

        self.fpga_offset = self.table.getIntegerTopic("FPGA Offset").subscribe(time.time())

        # Returns whether we have a tag
        self.has_tag = self.table.getBooleanTopic("AprilTag Presence").publish()

        # Global position of the robot
        # [x, y, theta]
        self.robot_global_pose = self.table.getDoubleArrayTopic("Robot Global Pose").publish()

        # Tag to camera transform (this is more useful than the raw pose)
        # [x, y, theta]
        self.tag_to_camera = self.table.getDoubleArrayTopic("Tag To Camera Pose").publish()

        # Raw tag center (just the raw center of the tag with no pose estimation.
        # Should be more stable when we're fine tuning our pose)
        # Is a value from -1 to 1
        #self.tag_center_x = self.table.getDoubleTopic("Tag Center X").publish()

        # Which tag is "best" (most centered)
        self.best_tag_id = self.table.getIntegerTopic("Best Tag ID").publish()

        self.pose_timestamp = self.table.getDoubleTopic("Global Pose Timestamp").publish()

    def set_values(self, has_tag: bool, robot_pose: Pose2d | None, best_tag: apriltag.Apriltag | None) -> None:
        """ Set important network tables values """
        self.has_tag.set(has_tag)

        # Publish global position
        if robot_pose is not None:
            self.robot_global_pose.set([robot_pose.x, robot_pose.y, robot_pose.rotation().radians()])
            self.pose_timestamp.set((time.time_ns() - self.fpga_offset.get()) / 1e9)

        if best_tag:
            # Publish local position & rotation

            # Calculate theta
            theta = best_tag.tag_to_camera.rotation().z
            theta -= numpy.sign(theta) * math.pi

            self.tag_to_camera.set([best_tag.tag_to_camera.x, best_tag.tag_to_camera.y, theta])

            # Other
            self.best_tag_id.set(best_tag.id)
            #self.tag_center_x.set(best_tag.detection.getCenter().x)
