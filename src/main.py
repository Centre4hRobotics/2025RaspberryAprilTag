""" This is the main file for FRC Team 4027's 2024 AprilTag Vision. """

import json
from wpimath.geometry import Pose3d

from apriltag import apriltag, apriltag_estimator
from net_table import network_tables
from camera import camera
import constants

#  Import all JSON settings
with open("config/Constants.json", encoding="utf-8") as file:
    settings = json.load(file)

#  All settings
IS_TABLE_HOST = settings["is table host"]
TEAM_NUMBER = settings["team number"]
CAMERAS = settings["cameras"]

# Set the blacklist/whitelist
FILTER = constants.List(settings)

# Camera Stuff
output_stream = camera.init_cameras(CAMERAS)

# Note: This may or may not work, I'm just guessing how cameras are assigned
cameras = [camera.Camera(2 * i, c) for i, c in enumerate(CAMERAS)]

# Create the PoseEstimator & adjust its settings
estimators = [apriltag_estimator.ApriltagEstimator(cam.calibration) for cam in cameras]

# Creating the network tables
tables = network_tables.NetworkTable(IS_TABLE_HOST, TEAM_NUMBER)

def main():
    """ Main loop"""
    robot_pose = Pose3d()

    best_tag = None

    while True:
        # Reset local variables
        has_tag = False

        # Update selections
        cam_index: int = tables.camera_choice.get()
        cam = cameras[cam_index]
        cam.update()

        detections = estimators[cam_index].detector.detect(cam.get_frame()) # type: ignore

        tags = [apriltag.Apriltag(detection) for detection in detections]

        # Change tags based on whitelist/blacklist
        tags = constants.verify_tags(FILTER, tags)

        if tags: # If there are tags to look at
            has_tag = True

            # Draw & undistort tags
            for tag in tags:
                tag.draw_corners(cam.get_frame(), constants.colors.detection)

                tag.undistort_corners(cam.calibration)

                tag.calculate_pose(estimators[cam_index])

            # Get most centered tag
            tag_x_pos = [x.x_dist(cam.calibration.x_res) for x in tags]
            best_tag_index = tag_x_pos.index(next((t for t in tags if tag_x_pos is min(tag_x_pos))))

            best_tag = tags[best_tag_index]
            best_tag.draw_corners(cam.get_frame(), constants.colors.best_detection)

            # Calculate global pose
            if best_tag.global_pose:
                camera_pose = best_tag.global_pose.transformBy(best_tag.tag_to_camera)
                robot_pose = camera_pose.transformBy(cam.offset)

        # Publish everything to network tables

        output_stream.putFrame(cam.get_frame())

        network_tables.set_values(tables,
            # General
            has_tag,
            robot_pose,
            # Centered Tag
            best_tag
        )

if __name__ == "__main__":
    main()
