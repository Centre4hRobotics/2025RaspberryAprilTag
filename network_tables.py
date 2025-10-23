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

        if is_host:
            nt_instance.startServer()

        else:
            nt_instance.setServerTeam(team_number)
            nt_instance.startClient4("visionPi")

        self.table = nt_instance.getTable("AprilTag Vision")

        # Returns whether we have a tag
        self.has_tag = self.table.getBooleanTopic("AprilTag Presence").publish()

        # Global position of the robot
        self.robot_global_pose = [
            self.table.getDoubleTopic("Global X").publish(),
            self.table.getDoubleTopic("Global Y").publish()
            #self.robot_z = self.table.getDoubleTopic("Global Z").publish()
        ]
        #self.robot_theta = self.table.getDoubleTopic("Global Theta").publish()

        # Tag to camera transform (this is more useful than the raw pose)
        self.tag_to_camera = [
            self.table.getDoubleTopic("TagToCamera X").publish(),
            self.table.getDoubleTopic("TagToCamera Y").publish(),
            #self.tag_to_camera_z = self.table.getDoubleTopic("TagToCamera Z").publish(),
            self.table.getDoubleTopic("TagToCamera Theta").publish()
        ]
        # Raw tag center (just the raw center of the tag with no pose estimation.
        # Should be more stable when we're fine tuning our pose)
        # Is a value from -1 to 1
        self.tag_center_x = self.table.getDoubleTopic("Tag Center X").publish()

        # Which tag is "best"
        self.best_tag_id = self.table.getIntegerTopic("Best Tag ID").publish()

        "Which camera to use"
        camera_topic = self.table.getIntegerTopic("Using Camera").publish()
        camera_topic.set(0)

        self.camera_choice = self.table.getIntegerTopic("Using Camera").subscribe(-1)

def set_values(table, has_tag, robot_pose, best_tag):
    """ Set important network tables values """
    table.has_tag.set(has_tag)
    # Publish global position
    table.robot_global_pose[0].set(robot_pose.x)
    table.robot_global_pose[1].set(robot_pose.y)
    #robot_z.set(robot_pose.z)

    if best_tag:
        # Publish local position & rotation
        table.tag_to_camera[0].set(best_tag.tag_to_camera.x)
        table.tag_to_camera[1].set(best_tag.tag_to_camera.y)

        z = best_tag.tag_to_camera.rotation().z

        table.tag_to_camera[3].set(
            z - numpy.sign(z) * math.pi
        )

        # Other
        table.best_tag_id.set(best_tag.id)
        table.tag_center_x.set(best_tag.detection.getCenter().x)
