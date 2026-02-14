""" Multi-tag robot pose detection """

import numpy
import cv2
from wpimath.geometry import Pose2d, Translation3d, Transform3d, Rotation3d, CoordinateSystem

from src.apriltag import apriltag
from src.camera import camera

half_tag = .5 * 6.5 * 25.4 * 1/1000 # 1/2 of tag size=(6.5" * 25.4mm/in * 1m/1000mm * 1/2)
corner_offsets = [
    Translation3d(0, -half_tag, -half_tag), # bottom left
    Translation3d(0, half_tag, -half_tag), # bottom right
    Translation3d(0, half_tag, half_tag), # top right
    Translation3d(0, -half_tag, half_tag) # top left
]

def multi_tag_pose(
        tags: list[apriltag.Apriltag],
        cam: camera.Camera,
        rvec: cv2.typing.MatLike | None = None,
        tvec: cv2.typing.MatLike | None = None
    ) -> tuple[Pose2d | None, tuple[cv2.typing.MatLike | None, cv2.typing.MatLike | None]]:

    """ Use SolvePNP to find the robot's pose. """

    # Get all corners
    screen_points = []
    world_points = []

    for tag in tags:
        if tag.global_pose:
            for i in range(4):
                world_points.append(
                    CoordinateSystem.convert(
                        (corner_offsets[i].rotateBy(tag.global_pose.rotation()) + tag.global_pose.translation()),
                        CoordinateSystem.NWU(), # From
                        CoordinateSystem.EDN()  # To
                    ).toVector()
                )
                screen_points.append([tag.corners[2 * i], tag.corners[2 * i + 1]])

    # Convert to numpy arrays (required for OpenCV)
    screen_points = numpy.array(screen_points)
    world_points = numpy.array(world_points)

    # SolvePnP requires 4 points (min)
    if len(world_points) < 4:
        return None, (rvec, tvec)

    # Distortions
    distortion = numpy.array(cam.calibration.camera_distortion)
    # Intrinsics
    intrinsics = numpy.array(cam.calibration.camera_intrinsics)

    # SolvePnP call (duh)
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

    if success:

        r, _ = cv2.Rodrigues(rvec)

        r_inv = r.T
        t_inv = -r.T @ tvec

        # Compose results into Transform3d
        inverse_transform = Transform3d(Translation3d(t_inv), Rotation3d(r_inv))

        # Convert back to NWU coordinate system
        inverse_transform = CoordinateSystem.convert(
            inverse_transform,
            CoordinateSystem.EDN(), # From
            CoordinateSystem.NWU() # To
        )

        # Include camera offset
        inverse_transform = inverse_transform + cam.offset.inverse()

        robot_rotation = inverse_transform.rotation()
        robot_pos = inverse_transform.translation()

        return Pose2d(robot_pos.toTranslation2d(), robot_rotation.toRotation2d()), (rvec, tvec)

    # Should only happen with extraneous tags
    return None, (None, None)
