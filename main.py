""" This is the main file for FRC Team 4027's 2024 AprilTag Vision. """

import subprocess
import json
import math
import numpy
import cv2
import robotpy_apriltag
from wpimath.geometry import Transform3d, Rotation3d, Pose3d, CoordinateSystem
from cscore import CameraServer

import camera_calibration
import apriltag_estimator
import network_tables
import camera

#  Import all JSON settings
with open("config/Constants.json", encoding="utf-8s") as file:
    settings = json.load(file)

#  All settings
IS_TABLE_HOST = settings["is table host"]
TEAM_NUMBER = settings["team number"]
FRAME_RATE = settings["fps"]
CAMERA_PROFILE = settings["camera_profile"]
    
# Loading the AprilTag data
aprilTag_field_layout = robotpy_apriltag.AprilTagFieldLayout(settings["tag poses"])

# Load camera calibration
calibration = camera_calibration.CameraCalibration(CAMERA_PROFILE)

# Create the PoseEstimator & adjust its settings
estimator = apriltag_estimator.ApriltagEstimator(calibration)

# Creating the network tables
tables = network_tables.NetworkTable(IS_TABLE_HOST, TEAM_NUMBER)

# Activate camera stuff
CameraServer.enableLogging()

# These should be an array, methinks - Sam
left_camera = camera.Camera(2, calibration)
right_camera = camera.Camera(0, calibration)

outputStream = CameraServer.putVideo("Vision", calibration.x_res, calibration.y_res)

# set camera settings (bash script)
rc = subprocess.call("chmod u+rx set_camera_settings.sh "
+ "&& /home/pi/2024RaspberryAprilTag/set_camera_settings.sh", shell = True)
print("set_camera_settings.sh returned: ", rc)

# Images
mat = numpy.zeros(shape=(calibration.x_res, calibration.y_res, 3), dtype=numpy.uint8)
gray_mat = numpy.zeros(shape=(calibration.x_res, calibration.y_res), dtype=numpy.uint8)

# Colors for drawing
line_color = (0,255,0)

# Etc.
robot_pose = Pose3d()
best_tag_to_camera = Transform3d()
best_tag_center_x = 0
best_tag = -1
theta = 0
REEF_TAGS = [6,7,8,9,10,11,17,18,19,20,21,22]

# Main loop
while True:
    has_tag = False

    if tables.camera_string.get() == "LEFT":
        _, mat = left_camera.cv_sink.grabFrame(mat)

    else:
        _, mat = right_camera.cv_sink.grabFrame(mat)

    # Bill: both cameras were upside down so I rotated them.
    mat = cv2.rotate(mat, cv2.ROTATE_180)
    gray_mat = cv2.cvtColor(mat, cv2.COLOR_RGB2GRAY)

    detections = estimator.apriltag_detector.detect(gray_mat)

    min_tag_x = 100000

    for detection in detections:

        tag = tables.tag_choice.get()
        if tag > 0 and detection.getId() != tag:
            continue

        # Remove detection if it is not a reef tag.
        if detection.getId() not in REEF_TAGS:
            continue # Move on to the next detection or exit the for loop
        corners = list(detection.getCorners(numpy.empty(8)))

        # Outline the tag using original corners
        for i in range(4):
            j = (i + 1) % 4
            p1 = (int(corners[2 * i]),int(corners[2 * i + 1]))
            p2 = (int(corners[2 * j]),int(corners[2 * j + 1]))
            mat = cv2.line(mat, p1, p2, line_color, 2)

        # Manually reshape 'corners'
        distorted_corners = numpy.empty([4,2], dtype=numpy.float32)
        for i in range(4):
            distorted_corners[i][0] = corners[2 * i]
            distorted_corners[i][1] = corners[2 * i + 1]

        # run the OpenCV undistortion routine to fix the corners
        undistorted_corners = cv2.undistortImagePoints(distorted_corners,
                                                       calibration.camera_intrinsics,
                                                       calibration.camera_distortion)
        for i in range(4):
            corners[2 * i] = undistorted_corners[i][0][0]
            corners[2 * i + 1] = undistorted_corners[i][0][1]

        if numpy.abs((2*detection.getCenter().x - calibration.x_res)/calibration.x_res) < min_tag_x:
            min_tag_x = numpy.abs((2*detection.getCenter().x - calibration.x_res)/calibration.x_res)
            best_detection = detection
            best_corners = corners

        has_tag = True

    if has_tag:
        # run the pose estimator using the fixed corners
        camera_to_tag = estimator.pose_estimator.estimate(
        homography = best_detection.getHomography(),
            corners = tuple(best_corners)
        )

        best_tag = best_detection.getId()

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

        best_tag_center_x = (2 * best_detection.getCenter().x - calibration.x_res) / calibration.x_res
        best_tag_to_camera = tag_to_camera
        best_color = (255,255,0)
        for i in range(4):
            j = (i + 1) % 4
            p1 = (int(best_corners[2 * i]),int(best_corners[2 * i + 1]))
            p2 = (int(best_corners[2 * j]),int(best_corners[2 * j + 1]))
            mat = cv2.line(mat, p1, p2, best_color, 2)

    # Publish everything

    outputStream.putFrame(mat)

    tables.set_values(
        robot_pose,
        best_tag_to_camera,
        theta,
        has_tag,
        best_tag,
        (best_tag_center_x,0)
    )
