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
        #robot_z = table.getDoubleTopic("Global Z").publish()

        # Tag to camera transform (this is more useful than the raw pose)
        self.tag_to_camera_x = self.table.getDoubleTopic("TagToCamera X").publish()
        self.tag_to_camera_y = self.table.getDoubleTopic("TagToCamera Y").publish()
        self.tag_to_camera_z = self.table.getDoubleTopic("TagToCamera Z").publish()
        self.tag_to_camera_theta = self.table.getDoubleTopic("TagToCamera Theta").publish()

        # Raw tag center (just the raw center of the tag with no pose estimation.
        # Should be more stable when we're fine tuning our pose)
        # Is a value from -1 to 1
        self.tag_center_x = self.table.getDoubleTopic("Tag Center X").publish()

        # Returns whether we have a tag
        self.has_tag = self.table.getBooleanTopic("AprilTag Presence").publish()

        self.best_tag_id = self.table.getIntegerTopic("Best Tag ID").publish()

        self.camera_choice = self.table.getStringTopic("Using Camera").publish()
        self.camera_choice.set("LEFT")

        self.camera_string = self.table.getStringTopic("Using Camera").subscribe("NO TABLE FOUND")

        self.tag_choice_topic = self.table.getIntegerTopic("Tag Choice").publish()
        self.tag_choice_topic.set(0)

        self.tag_choice = self.table.getIntegerTopic("Tag Choice").subscribe(0)

    def set_values(self, robot_pose, tag_to_camera, ttc_theta, has_tag, best_tag_id, best_tag_center):

        # Publish global position
        self.robot_x.set(robot_pose.x)
        self.robot_y.set(robot_pose.y)
        #robot_z.set(robot_pose.z)

        # Publish local position & rotation
        self.tag_to_camera_x.set(tag_to_camera.x)
        self.tag_to_camera_y.set(tag_to_camera.y)

        self.tag_to_camera_theta.set(ttc_theta)

        # Other
        self.has_tag.set(has_tag)
        self.best_tag_id.set(best_tag_id)
        self.tag_center_x.set(best_tag_center[0])