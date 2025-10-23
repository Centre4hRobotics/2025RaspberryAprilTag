""" Network tables handling code """

import math
import numpy
import ntcore

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

        # Export robot position

        # Global position of the robot
        self.robot_x = self.table.getDoubleTopic("Global X").publish()
        self.robot_y = self.table.getDoubleTopic("Global Y").publish()
        #self.robot_z = self.table.getDoubleTopic("Global Z").publish()
        #self.robot_theta = self.table.getDoubleTopic("Global Theta").publish()

        # Tag to camera transform (this is more useful than the raw pose)
        self.tag_to_camera_x = self.table.getDoubleTopic("TagToCamera X").publish()
        self.tag_to_camera_y = self.table.getDoubleTopic("TagToCamera Y").publish()
        #self.tag_to_camera_z = self.table.getDoubleTopic("TagToCamera Z").publish()
        self.tag_to_camera_theta = self.table.getDoubleTopic("TagToCamera Theta").publish()

        # Raw tag center (just the raw center of the tag with no pose estimation.
        # Should be more stable when we're fine tuning our pose)
        # Is a value from -1 to 1
        self.tag_center_x = self.table.getDoubleTopic("Tag Center X").publish()

        # Returns whether we have a tag
        self.has_tag = self.table.getBooleanTopic("AprilTag Presence").publish()

        self.best_tag_id = self.table.getIntegerTopic("Best Tag ID").publish()

        self.camera_topic = self.table.getIntegerTopic("Using Camera").publish()
        self.camera_topic.set(0)

        self.camera_choice = self.table.getIntegerTopic("Using Camera").subscribe(-1)

        self.tag_choice_topic = self.table.getIntegerTopic("Tag Choice").publish()
        self.tag_choice_topic.set(0)

        self.tag_choice = self.table.getIntegerTopic("Tag Choice").subscribe(0)

    def set_values(self, has_tag, robot_pose, best_tag):
        """ Set important network tables values """
        self.has_tag.set(has_tag)
        # Publish global position
        self.robot_x.set(robot_pose.x)
        self.robot_y.set(robot_pose.y)
        #robot_z.set(robot_pose.z)

        if best_tag:
            # Publish local position & rotation
            self.tag_to_camera_x.set(best_tag.tag_to_camera.x)
            self.tag_to_camera_y.set(best_tag.tag_to_camera.y)

            z = best_tag.tag_to_camera.rotation().z

            self.tag_to_camera_theta.set(
                z - numpy.sign(z) * math.pi
            )

            # Other
            self.best_tag_id.set(best_tag.id)
            self.tag_center_x.set(best_tag.detection.getCenter().x)
