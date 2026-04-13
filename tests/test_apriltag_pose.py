""" Tests for individual AprilTag detection and coordinate system math. """
from unittest.mock import MagicMock
import math

import pytest
import numpy
from wpimath.geometry import Pose3d, Rotation3d, Translation3d, Transform3d

from src import apriltag

class TestApriltag:
    """ Groups unit tests for individual AprilTag detection and coordinate math. """

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
        ]
    )
    def test_undistort_logic_integrity(self, mock_tag, mock_camera, tag_pose):
        """ Verifies that if our camera has 'perfect' lenses (zero distortion),
            the code doesn't accidentally move or warp the tag's corners. """

        tag = mock_tag(tag_pose, Pose3d())
        tag.undistort_corners(mock_camera.calibration)

        # Since distortion is 0, the 'cleaned up' corners should match the original ones
        for i in range(8):
            assert tag.undistorted_corners[i] == pytest.approx(tag.corners[i], abs=1e-3)

    #@pytest.mark.parametrize(
    #    "camera_pose, tag_pose",
    #    [
    #       (Pose3d(Translation3d(1, 0, 0), Rotation3d(0, 0, math.pi)), Pose3d())
    #   ]
    #)
    #def test_ttc(self, mock_tag, mock_camera, camera_pose, tag_pose):
    #    """ Ensure tag-to-camera transform is calculated correctly """

    #    tag = mock_tag(tag_pose, camera_pose)

    #    tag.undistort_corners(mock_camera.calibration)

    #    tag_to_camera = tag.calculate_pose(apriltag.apriltag_estimator.ApriltagEstimator(mock_camera.calibration))

    #    expected = tag.global_pose.transformBy(tag_to_camera)

    #    assert expected.X() == pytest.approx(camera_pose.X(), abs=0.01)
    #    assert expected.Y() == pytest.approx(camera_pose.Y(), abs=0.01)
    #    assert expected.Z() == pytest.approx(camera_pose.Z(), abs=0.01)
    #    print(tag_to_camera)
        # Check rotation
        # 0 = facing tag
    #    theta = tag_to_camera.rotation().Z()
    #    theta -= numpy.sign(theta) * math.pi

        # expected rotation

    #    expected_theta = Transform3d(camera_pose, tag_pose).rotation().Z()
    #    expected_theta -= numpy.sign(expected_theta) * math.pi

    #    assert theta == pytest.approx(expected_theta, abs=0.05)
