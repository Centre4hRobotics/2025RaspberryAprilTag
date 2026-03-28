""" Tests for individual AprilTag detection and coordinate system math. """
from unittest.mock import MagicMock

import pytest
import numpy as np
from wpimath.geometry import Pose3d, Rotation3d, Transform3d, Translation3d
import robotpy_apriltag

from src import apriltag

class TestApriltag:
    """ Groups unit tests for individual AprilTag detection and coordinate math. """

    # --- Fixtures ---

    @pytest.fixture
    def mock_field(self):
        """ Creates a fake 'map' of the field where an AprilTag is sitting
            exactly at the center (0,0,0). """
        field = MagicMock(spec=robotpy_apriltag.AprilTagFieldLayout)
        field.getTagPose.return_value = Pose3d(Translation3d(0, 0, 0), Rotation3d())
        return field

    # --- Tests ---

    @pytest.mark.parametrize(
        "center_x, expected_dist",
        [
            (640, 0.0),   # Center of 1280 is 640
            (0, -1.0),     # Left side results in -1.0
            (1280, 1.0),   # Right side results in 1.0
            (960, 0.5),    # Halfway between center and right edge
        ],
        ids=["Perfectly Centered", "Far Left Edge", "Far Right Edge", "Quarter Right"]
    )
    def test_x_dist_calculation(self, center_x, expected_dist):
        """ Checks if the code correctly calculates how far left or right a tag
            is on the screen, ranging from -1.0 (left) to 1.0 (right). """
        detection = MagicMock()
        detection.getCenter.return_value = MagicMock(x=center_x)

        # We don't need a real field layout for this specific math check
        tag = apriltag.Apriltag(detection, MagicMock())

        assert tag.x_dist(1280) == pytest.approx(expected_dist)

    @pytest.mark.parametrize(
        "tag_pose",
        [
            (Pose3d(Translation3d(1, 0, 0), Rotation3d())),
            (Pose3d(Translation3d(1, 0, 0), Rotation3d(0, 0, 0.75)))
        ],
        ids=["Standard Square", "Centered Square"]
    )
    def test_undistort_logic_integrity(self, mock_tag, mock_camera, tag_pose):
        """ Verifies that if our camera has 'perfect' lenses (zero distortion),
            the code doesn't accidentally move or warp the tag's corners. """

        tag = mock_tag(tag_pose, Pose3d())
        tag.undistort_corners(mock_camera.calibration)

        # Since distortion is 0, the 'cleaned up' corners should match the original ones
        for i in range(8):
            assert tag.undistorted_corners[i] == pytest.approx(tag.corners[i], abs=1e-3)

    @pytest.mark.parametrize(
        "camera_pose",
        [
            (Pose3d(Translation3d(1, 0, 0), Rotation3d(0, 0, 3.14)))
        ]
    )
    def test_coordinate_system_conversion_logic(self, mock_tag, mock_camera, camera_pose):
        """
        Tests the logic that converts raw camera data into a 3D position.

        It handles three steps:
        1. OpenCV View: (X=Right, Y=Down, Z=Forward)
        2. Robot View:  (X=Forward, Y=Left, Z=Up)
        3. The 'Inverse': Flips the perspective from 'Where is the tag?' to 'Where is the camera?'
        """
        # 1. Simulate a tag that is exactly 1 meter directly in front of the camera
        estimator = apriltag.apriltag_estimator.ApriltagEstimator(mock_camera.calibration)

        tag = mock_tag(Pose3d(), camera_pose)

        # 2. Run the math to convert the coordinates
        result_transform = tag.calculate_pose(estimator)

        # 3. Validation:
        # If the tag was 1 meter in front of the camera, then from the tag's
        # perspective, the camera is 1 meter away on the X-axis (Forward).
        assert result_transform.X() == pytest.approx(camera_pose.X(), abs=0.01)
        assert result_transform.Y() == pytest.approx(camera_pose.Y(), abs=0.01)
        assert result_transform.Z() == pytest.approx(camera_pose.Z(), abs=0.01)

    @pytest.mark.parametrize(
        "tag_pose",
        [
            (Pose3d(Translation3d(1, 0, 0), Rotation3d()),)
        ]
    )
    def test_ttc(self, mock_camera, mock_tag, tag_pose):
        """ Test if tag-to-camera transforms work properly """
