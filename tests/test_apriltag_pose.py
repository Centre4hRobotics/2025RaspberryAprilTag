""" Tests for individual AprilTag detection and coordinate system math. """
import pytest
import numpy as np
from unittest.mock import MagicMock
from wpimath.geometry import Pose3d, Rotation3d, Transform3d, Translation3d
import robotpy_apriltag

from src.apriltag.apriltag import Apriltag

class TestApriltag:
    """ Groups unit tests for individual AprilTag detection and coordinate math. """

    # --- Fixtures ---

    @pytest.fixture
    def mock_calibration(self):
        """ Creates a fake camera setup with a standard resolution (1280x720) 
            and no lens distortion to make testing math easier. """
        calib = MagicMock()
        calib.x_res = 1280
        calib.y_res = 720
        # The 'intrinsics' matrix tells the code how to turn 3D points into 2D pixels
        calib.camera_intrinsics = np.array([
            [600, 0, 640],
            [0, 600, 360],
            [0, 0, 1]
        ], dtype=np.float32)
        # Distortion is set to zero so the image isn't 'warped' in these tests
        calib.camera_distortion = np.zeros(5, dtype=np.float32)
        return calib

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
        tag = Apriltag(detection, MagicMock())
        
        assert tag.x_dist(1280) == pytest.approx(expected_dist)

    @pytest.mark.parametrize(
        "raw_corners",
        [
            ((300, 300, 400, 300, 400, 400, 300, 400)),
            ((640, 360, 740, 360, 740, 460, 640, 460))
        ],
        ids=["Standard Square", "Centered Square"]
    )
    def test_undistort_logic_integrity(self, raw_corners, mock_field, mock_calibration):
        """ Verifies that if our camera has 'perfect' lenses (zero distortion), 
            the code doesn't accidentally move or warp the tag's corners. """
        detection = MagicMock()
        detection.getCorners.return_value = raw_corners
        detection.getId.return_value = 1
        
        tag = Apriltag(detection, mock_field)
        tag.undistort_corners(mock_calibration)
        
        # Since distortion is 0, the 'cleaned up' corners should match the original ones
        for i in range(8):
            assert tag.undistorted_corners[i] == pytest.approx(raw_corners[i], abs=1e-3)

    def test_coordinate_system_conversion_logic(self, mock_field):
        """
        Tests the logic that converts raw camera data into a 3D position.
        
        It handles three steps:
        1. OpenCV View: (X=Right, Y=Down, Z=Forward)
        2. Robot View:  (X=Forward, Y=Left, Z=Up)
        3. The 'Inverse': Flips the perspective from 'Where is the tag?' to 'Where is the camera?'
        """
        # 1. Simulate a tag that is exactly 1 meter directly in front of the camera
        mock_estimator = MagicMock()
        # EDN = (X: Right, Y: Down, Z: Forward)
        edn_pose = Transform3d(Translation3d(0, 0, 1), Rotation3d())
        mock_estimator.pose_estimator.estimate.return_value = edn_pose
        
        detection = MagicMock()
        detection.getHomography.return_value = np.eye(3)
        detection.getCorners.return_value = (0, 0, 0, 0, 0, 0, 0, 0)
        detection.getId.return_value = 1
        
        tag = Apriltag(detection, mock_field)
        
        # 2. Run the math to convert the coordinates
        result_transform = tag.calculate_pose(mock_estimator)
        
        # 3. Validation:
        # If the tag was 1 meter in front of the camera, then from the tag's 
        # perspective, the camera is 1 meter away on the X-axis (Forward).
        assert result_transform.translation().x == pytest.approx(1.0)
        assert result_transform.translation().y == pytest.approx(0.0)
        assert result_transform.translation().z == pytest.approx(0.0)