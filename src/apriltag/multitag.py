""" Multi-tag robot pose detection """

import numpy
import cv2
from wpimath.geometry import Pose2d, Translation2d, Rotation2d, Translation3d, Transform3d, Rotation3d, CoordinateSystem

from src.apriltag import apriltag
from src.camera import camera

def multi_tag_pose(tags: list[apriltag.Apriltag], cam: camera.Camera, rvec, tvec):
    """ Use SolvePNP to find the robot's pose. """

    half_tag = .5 * 6.5 * 25.4 * 1/1000 # 1/2 of tag size=(6.5" * 25.4mm/in * 1m/1000mm * 1/2)
    corner_offsets = [
        Translation3d(0, -half_tag, -half_tag), # bottom left
        Translation3d(0, half_tag, -half_tag), # bottom right
        Translation3d(0, half_tag, half_tag), # top right
        Translation3d(0, -half_tag, half_tag) # top left
    ]

    # Get all corners
    screen_points = []
    world_points = []
    for tag in tags:
        if tag.global_pose:
            for i in range(4):
                world_points.append(CoordinateSystem.convert((corner_offsets[i].rotateBy(tag.global_pose.rotation()) + tag.global_pose.translation()), CoordinateSystem.NWU(), CoordinateSystem.EDN()).toVector())
                screen_points.append([tag.corners[2 * i], tag.corners[2 * i + 1]])

    screen_points = numpy.array(screen_points)
    world_points = numpy.array(world_points)

    if len(world_points) < 4:
        return None, rvec, tvec

    # Distortions
    distortion = numpy.array(cam.calibration.camera_distortion)
    # Intrinsics
    intrinsics = numpy.array(cam.calibration.camera_intrinsics)
    print(intrinsics)

    success, rvec, tvec = cv2.solvePnP(
        world_points,
        screen_points,
        intrinsics,
        distortion,
        rvec=rvec,
        tvec=tvec,
        useExtrinsicGuess=(rvec is not None and tvec is not None),
        flags=cv2.SOLVEPNP_ITERATIVE
    )

    #cam_to_robot = cam.offset.inverse()

    if success:

        R, _ = cv2.Rodrigues(rvec)

        R_inv = R.T
        t_inv = -R.T @ tvec

        inverse_transform = Transform3d(Translation3d(t_inv), Rotation3d(R_inv))
        inverse_transform = CoordinateSystem.convert(inverse_transform, CoordinateSystem.EDN(), CoordinateSystem.NWU())
        robot_pos_world = inverse_transform.translation()

        x = robot_pos_world.x
        y = robot_pos_world.y

        print('screen points:')
        print(screen_points)

        return Pose2d(Translation2d(x, y), Rotation2d()), rvec, tvec

    return None, None, None
