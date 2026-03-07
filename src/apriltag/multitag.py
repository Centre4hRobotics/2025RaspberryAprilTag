""" Multi-tag robot pose detection """

import numpy
import cv2
from wpimath.geometry import Pose2d, Translation3d, Pose3d, Rotation3d

from src import apriltag, camera

HALF_TAG = .5 * 6.5 * 25.4 * 1/1000 # 1/2 of tag size=(6.5" * 25.4mm/in * 1m/1000mm * 1/2)
corner_offsets = [
    Translation3d(0, -HALF_TAG, -HALF_TAG), # bottom left
    Translation3d(0, HALF_TAG, -HALF_TAG), # bottom right
    Translation3d(0, HALF_TAG, HALF_TAG), # top right
    Translation3d(0, -HALF_TAG, HALF_TAG) # top left
]

def pose_from_vecs(rvec: cv2.typing.MatLike, tvec: cv2.typing.MatLike) -> Pose2d:
    """ Calculate pose from rvec and tvec given by SolvePnP """
    r, _ = cv2.Rodrigues(rvec)

    r_inv = r.T
    t_inv = -r_inv @ tvec

    # Compose results into Transform3d
    inverse_transform = Pose3d(Translation3d(t_inv), Rotation3d(r_inv))

    return inverse_transform.toPose2d()

def multi_tag_pose(
        tags: list[apriltag.Apriltag],
        cam: camera.Camera,
        rvec: cv2.typing.MatLike | None = None,
        tvec: cv2.typing.MatLike | None = None
    ) -> tuple[Pose2d | None, tuple[cv2.typing.MatLike | None, cv2.typing.MatLike | None]]:

    """ Use SolvePNP to find the camera's global pose. """

    # Get all corners
    screen_points = []
    world_points = []

    for tag in tags:
        if tag.global_pose:
            for i in range(4):
                world_points.append(
                    #CoordinateSystem.convert(
                        (corner_offsets[i].rotateBy(tag.global_pose.rotation()) + tag.global_pose.translation())
                    #    CoordinateSystem.NWU(), # From
                    #    CoordinateSystem.EDN()  # To
                    .toVector()
                )
                screen_points.append([tag.corners[2 * i], tag.corners[2 * i + 1]])

    # Convert to numpy arrays (required for OpenCV)
    screen_points = numpy.array(screen_points, dtype=numpy.float32)
    world_points = numpy.array(world_points, dtype=numpy.float32)

    # SolvePnP requires 4 points (min)
    if len(world_points) < 4:
        return None, (rvec, tvec)

    # Convert camera constants to usable format
    distortion = numpy.array(cam.calibration.camera_distortion)
    intrinsics = numpy.array(cam.calibration.camera_intrinsics)

    # SolvePnP call (duh)
    success, new_rvec, new_tvec = cv2.solvePnP(
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

        new_pose = pose_from_vecs(new_rvec, new_tvec)

        if rvec is not None and tvec is not None:
            old_pose = pose_from_vecs(rvec, tvec)
            if old_pose.translation().distance(new_pose.translation()) >= 0.5 and len(world_points) < 8:
                return None, (rvec, tvec)

        return new_pose, (new_rvec, new_tvec)

    # Should only happen with extraneous tags
    return None, (rvec, tvec)
