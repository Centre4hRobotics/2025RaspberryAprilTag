""" Tests Multi-Tag Pose Computation with SolvePnP """

from unittest.mock import MagicMock

import pytest
from wpimath.geometry import Pose3d, Rotation3d, Translation3d, CoordinateSystem

from src.apriltag.multitag import multi_tag_pose, pose_from_vecs
from src import camera
from cameras import virtual_capture

def world_to_cam_point(intrinsics, cam_pose: Pose3d, world_point: Translation3d) -> tuple[int, int]:
    """ Convert a world position into a screen position """

    # Convert both the camera pose and world point into EDN
    cv_cam_pose = CoordinateSystem.convert(cam_pose, CoordinateSystem.NWU(), CoordinateSystem.EDN())
    cv_world_point = CoordinateSystem.convert(world_point, CoordinateSystem.NWU(), CoordinateSystem.EDN())

    # Express world point in camera frame
    p_cam = cv_world_point - cv_cam_pose.translation()
    p_cam = p_cam.rotateBy(-cv_cam_pose.rotation())

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

    points = []
    for i in range(4):
        points.append((corner_offsets[i].rotateBy(pose.rotation()) + pose.translation()))

    return points

def fake_tag(tag_pose: Pose3d, camera_pose: Pose3d, camera_: camera.Camera):
    """ Creates a mock AprilTag at a fixed world position. """
    tag = MagicMock()
    # Tag is at (5, 5, 0) in the world
    tag.global_pose = tag_pose # Pose3d(Translation3d(5, 5, 0), Rotation3d(0, 0, 0))
    # 2D corners on screen
    corners = []

    for corner in tag_pose_to_corners(tag_pose):
        x, y = world_to_cam_point(camera_.calibration.camera_intrinsics, camera_pose, corner)
        corners.append(x)
        corners.append(y)

    tag.corners = corners

    return tag

class TestMultiTagPose:
    """ Tests the SolvePnP wrapper for multi-tag robot localization. """

    # --- Fixtures ---

    @pytest.fixture
    def mock_camera(self):
        """ Creates a mock camera with standard calibration matrices. """

        settings = camera.settings.CameraSettings(
            {
                "resolution": {
                    "x": 1280,
                    "y": 800
                },
                "intrinsics": { "Fx": 1000, "Fy": 1000, "Cx": 640, "Cy": 400 },
                "distortion": [ 0, 0, 0, 0, 0 ],
                "rotation": 0
            }
        )

        cam = camera.Camera(settings, virtual_capture.VirtualCapture())

        return cam

    # --- Tests ---

    def test_solvepnp_once(self, mock_camera):
        """ Make sure solvePnP gets the right position """
        cam_true_pose = Pose3d(Translation3d(0, 0, 0), Rotation3d(0, 0, 0))
        tag_pose = Pose3d(Translation3d(2, 0, 0), Rotation3d(0, 0, 3.14159))

        tag = fake_tag(tag_pose, cam_true_pose, mock_camera)

        pose, _ = multi_tag_pose([tag], mock_camera, None, None)

        assert pose.X() == pytest.approx(cam_true_pose.X(), abs=0.05)
        assert pose.Y() == pytest.approx(cam_true_pose.Y(), abs=0.05)
        assert pose.rotation().radians() == pytest.approx(cam_true_pose.rotation().Z(), abs=0.05)

    def test_rejection_of_jumps(self, mock_camera):
        cam_true_pose = Pose3d(Translation3d(0, 0, 0), Rotation3d(0, 0, 0))
        tag_1_pose = Pose3d(Translation3d(2, 0, 0), Rotation3d(0, 0, 3.14159))

        tag_2_pose = Pose3d(Translation3d(10, 0, 0), Rotation3d(0, 0, 3.14159))

        tag = fake_tag(tag_1_pose, cam_true_pose, mock_camera)

        pose, (rvec, tvec) = multi_tag_pose([tag], mock_camera, None, None)

        assert pose is not None

        tag = fake_tag(tag_2_pose, cam_true_pose, mock_camera)
        tag.global_pose = tag_1_pose

        pose, (rvec, tvec) = multi_tag_pose([tag], mock_camera, rvec=rvec, tvec=tvec)

        assert pose is None
