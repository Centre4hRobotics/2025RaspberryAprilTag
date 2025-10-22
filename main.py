""" This is the main file for FRC Team 4027's 2024 AprilTag Vision. """

import json
import math
import numpy
import robotpy_apriltag
from wpimath.geometry import Transform3d, Rotation3d, Pose3d, CoordinateSystem

import apriltag_estimator
import network_tables
import camera
import apriltag
import constants

#  Import all JSON settings
with open("config/Constants.json", encoding="utf-8s") as file:
    settings = json.load(file)

#  All settings
IS_TABLE_HOST = settings["is table host"]
TEAM_NUMBER = settings["team number"]
CAMERAS = settings["cameras"]

if settings["whitelist"] is not None and settings["blacklist"] is not None:
    raise ValueError("Whitelist and Blacklist are both set!")
elif settings["blacklist"] is not None:
    LIST = settings["blacklist"]
    LIST_TYPE = constants.ListType.BLACKLIST
elif settings["whitelist"] is not None:
    LIST = settings["whitelist"]
    LIST_TYPE = constants.ListType.WHITELIST
else:
    LIST = []
    LIST_TYPE = constants.ListType.BLACKLIST

# Camera Stuff
# Activate camera stuff
output_stream = camera.init_cameras(CAMERAS)

cameras: list[camera.Camera] = []

# Note: this may or may not work; I'm just guessing how camera numbers are assigned.
for index, cam in enumerate(CAMERAS):
    cameras.append(camera.Camera(2 * index, cam))

# Loading the AprilTag data
aprilTag_field_layout = robotpy_apriltag.AprilTagFieldLayout(settings["tag poses"])

# Create the PoseEstimator & adjust its settings
estimators = [apriltag_estimator.ApriltagEstimator(cam.calibration) for cam in cameras]

# Creating the network tables
tables = network_tables.NetworkTable(IS_TABLE_HOST, TEAM_NUMBER)

# Colors for drawing
colors = constants.Colors()

# Etc.


def main():
    """ Main loop"""

    robot_pose = Pose3d()
    best_tag_to_camera = Transform3d()
    best_tag_center_x = 0
    best_tag = -1
    theta = 0

    while True:
        # Reset local variables
        has_tag = False

        # Update selections
        cam_index = tables.camera_choice.get()
        current_camera = cameras[cam_index]
        current_camera.update()

        detections = estimators[cam_index].apriltag_detector.detect(current_camera.get_frame())

        tags: list[apriltag.Apriltag] = [apriltag.Apriltag(detection) for detection in detections]

        # Change 'tags' based on whitelist/blacklist
        if LIST_TYPE is constants.ListType.WHITELIST:
            tags = [t for t in tags if t.id in LIST] # remove elements which aren't in the list
        else: # If blacklist
            tags = [t for t in tags if t.id not in LIST] # remove elements which are in the list

        # If there are tags to look at
        if tags is not []:

            # Draw & undistort tags
            for tag in tags:
                tag.draw_corners(current_camera.get_frame(), colors.detection)

                tag.undistort_corners(current_camera.calibration)

            # Get most centered tag
            min_tag_x = min([x.x_dist(current_camera.calibration.x_res) for x in tags])
            centered_tag = next((t for t in tags if t.x_dist(current_camera.calibration.x_res) is min_tag_x), None)

            # run the pose estimator using the fixed corners
            camera_to_tag = estimators[cam_index].pose_estimator.estimate(
            homography = centered_tag.detection.getHomography(),
                corners = tuple(centered_tag.undistorted_corners)
            )

            best_tag = centered_tag.id

            # First, we flip the camera_to_tag transform's angle 180 degrees around the y axis
            # since the tag is oriented into the field
            flip_tag_rotation = Rotation3d(axis = (0, 1, 0), angle = math.pi)
            camera_to_tag = Transform3d(camera_to_tag.translation(),
                                        camera_to_tag.rotation().rotateBy(flip_tag_rotation))

            # The Camera To Tag transform is in a East/Down/North coordinate system,
            # but we want it in the WPILib standard North/West/Up
            camera_to_tag = CoordinateSystem.convert(camera_to_tag,
                                                    CoordinateSystem.EDN(),
                                                    CoordinateSystem.NWU())

            tag_to_camera = camera_to_tag.inverse()

            # Check if this tag is both the current best, and is in reef_tags
            theta = tag_to_camera.rotation().z
            theta -= numpy.sign(theta) * math.pi

            best_tag_center_x = (2 * centered_tag.detection.getCenter().x - current_camera.calibration.x_res) / current_camera.calibration.x_res
            best_tag_to_camera = tag_to_camera
            centered_tag.draw_corners(current_camera.get_frame(), colors.best_detection)

        # Publish everything

        outputStream.putFrame(current_camera.get_frame())

        tables.set_values(
            robot_pose,
            best_tag_to_camera,
            theta,
            has_tag,
            best_tag,
            (best_tag_center_x,0)
        )

if __name__ == "__main__":
    main()
