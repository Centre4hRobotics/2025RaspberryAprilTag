""" Multi-tag robot pose detection """

import math
import numpy
import cv2
from wpimath.geometry import Pose2d, Translation2d, Rotation2d

from src.apriltag import apriltag
from src.camera import camera


def multi_tag_pose(tags: list[apriltag.Apriltag], cam: camera.Camera) -> Pose2d:
    """ Use SolvePNP to find the robot's pose. """

    # World Points (corners of tags)
    world_points = numpy.array([
        t.global_pose.translation().toVector()
        for t in tags if t.global_pose
    ])

    # Screen points (corners of tags)
    screen_points = numpy.array([
        [t.detection.getCenter().x, t.detection.getCenter().y]
        for t in tags if t.global_pose
    ])

    if len(world_points) < 3:
        return Pose2d()

    # Distortions
    distortion = numpy.array(cam.calibration.camera_distortion)

    # Intrinsics
    intrinsics = numpy.array(cam.calibration.camera_intrinsics)

    success, rvec, tvec = cv2.solvePnP(world_points, screen_points, intrinsics, distortion)

    cam_offset_robot = cam.offset.translation().toVector()

    if success:
        rotation_matrix, _ = cv2.Rodrigues(rvec)

        cam_pos_world = -rotation_matrix.T @ tvec

        cam_rot_world = rotation_matrix.T

        cam_yaw_world = math.atan2(cam_rot_world[1, 0], cam_rot_world[0, 0])

        cam_offset_world = rotation_matrix.T @ cam_offset_robot

        robot_pos_world = cam_pos_world - cam_offset_world

        robot_yaw = cam_yaw_world - cam.offset.rotation().angle

        x, y, _ = robot_pos_world.reshape(3)

        return Pose2d(Translation2d(float(x), float(y)), Rotation2d(robot_yaw))

    return Pose2d()
