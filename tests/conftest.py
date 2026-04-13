""" Define basic, shared fixtures for all tests """

from unittest.mock import MagicMock

import pytest

import numpy
import cv2
from wpimath.geometry import Pose3d, CoordinateSystem, Translation3d

from src import camera, apriltag
from cameras import virtual_capture

@pytest.fixture(params=[{ "Fx": 1000, "Fy": 1000, "Cx": 640, "Cy": 400 }])
def mock_camera(request):
    """ Creates a mock camera with standard calibration matrices. """

    settings = camera.settings.CameraSettings(
        {
            "resolution": {
                "x": 1280,
                "y": 800
            },
            "intrinsics": request.param,
            "distortion": [ 0, 0, 0, 0, 0 ],
            "rotation": 0
        }
    )

    cam = camera.Camera(settings, virtual_capture.VirtualCapture())

    return cam

@pytest.fixture
def mock_tag(mock_camera):
    """ Creates a mock AprilTag at a fixed world position. """
    def _make(tag_pose: Pose3d, camera_pose: Pose3d, tag_id: int = 0):

        detection = MagicMock()

        corners = tag_pose_to_corners(tag_pose)
        screen_corners = [
            list(world_to_cam_point(mock_camera.calibration.camera_intrinsics, camera_pose, corner))
            for corner in corners
        ]

        detection.getCorners.return_value = tuple([
            coord
            for corner in screen_corners
            for coord in corner
        ])

        ideal_corners = [
            [-1, 1],
            [1, 1],
            [1, -1],
            [-1, -1]
        ]

        screen_corners.reverse()

        ideal_corners = numpy.array(ideal_corners, dtype=numpy.float32)
        screen_corners = numpy.array(screen_corners, dtype=numpy.float32)

        homography = cv2.getPerspectiveTransform(ideal_corners, screen_corners)
        detection.getHomography.return_value = tuple(homography.flatten())

        detection.getId.return_value = tag_id

        field = MagicMock()
        field.getTagPose.return_value = tag_pose

        tag = apriltag.Apriltag(detection, field)

        return tag
    return _make


def world_to_cam_point(intrinsics, cam_pose: Pose3d, world_point: Translation3d) -> tuple[int, int]:
    """ Convert a world position into a screen position """

    # Convert both the camera pose and world point into EDN
    cv_cam_pose = CoordinateSystem.convert(cam_pose, CoordinateSystem.NWU(), CoordinateSystem.EDN())
    cv_world_point = CoordinateSystem.convert(world_point, CoordinateSystem.NWU(), CoordinateSystem.EDN())

    # Express world point in camera frame
    p_cam = cv_world_point - cv_cam_pose.translation()

    X, Y, Z = p_cam.X(), p_cam.Y(), p_cam.Z()

    Fx = intrinsics[0][0]
    Fy = intrinsics[1][1]
    Cx = intrinsics[0][2]
    Cy = intrinsics[1][2]
    u = int(Fx * (X / Z) + Cx)
    v = int(Fy * (Y / Z) + Cy)

    return u, v

HALF_TAG = .5 * 6.5 * 25.4 * 1/1000 # 1/2 of tag size=(6.5" * 25.4mm/in * 1m/1000mm * 1/2)

def tag_pose_to_corners(pose: Pose3d) -> list[Translation3d]:
    """ Convert tag's world pose to corners """
    corner_offsets = [
        Translation3d(0, -HALF_TAG, -HALF_TAG), # bottom left
        Translation3d(0, HALF_TAG, -HALF_TAG), # bottom right
        Translation3d(0, HALF_TAG, HALF_TAG), # top right
        Translation3d(0, -HALF_TAG, HALF_TAG) # top left
    ]

    points = [corner_offset.rotateBy(pose.rotation()) + pose.translation() for corner_offset in corner_offsets]

    return points
