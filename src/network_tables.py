""" Network tables handling code """

import math
import dataclasses
import numpy
import ntcore

@dataclasses.dataclass
class NetworkTable:
    """ Wrap network tables """
    def __init__(self, is_host, team_number=4027):

        nt_instance = ntcore.NetworkTableInstance.getDefault()

        # If this is hosting, start the server. Else, join the server
        if is_host:
            nt_instance.startServer()
        else:
            nt_instance.setServerTeam(team_number)
            nt_instance.startClient4("visionPi")

        self.table = nt_instance.getTable("AprilTag Vision")

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
        self.tag_center_x = self.table.getDoubleTopic("Tag Center X").publish()

        # Which tag is "best"
        self.best_tag_id = self.table.getIntegerTopic("Best Tag ID").publish()

        # Which camera to use (0-indexed)
        camera_topic = self.table.getIntegerTopic("Using Camera").publish()
        camera_topic.set(0)
        self.camera_choice = self.table.getIntegerTopic("Using Camera").subscribe(-1)

    def set_values(self, has_tag, robot_pose, best_tag):
        """ Set important network tables values """
        self.has_tag.set(has_tag)
        # Publish global position
        self.robot_global_pose.set([robot_pose.x, robot_pose.y])
        #robot_z.set(robot_pose.z)

        if best_tag:
            # Publish local position & rotation

            # Calculate theta
            theta = best_tag.tag_to_camera.rotation().z
            theta -= numpy.sign(theta) * math.pi

            self.tag_to_camera.set([best_tag.tag_to_camera.x, best_tag.tag_to_camera.y, theta])

            # Other
            self.best_tag_id.set(best_tag.id)
            self.tag_center_x.set(best_tag.detection.getCenter().x)
