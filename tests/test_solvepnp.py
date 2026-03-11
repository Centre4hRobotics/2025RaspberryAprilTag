""" Tests Multi-Tag Pose Computation with SolvePnP """
import pytest
import numpy as np
import cv2
from unittest.mock import MagicMock
from wpimath.geometry import Pose3d, Rotation3d, Translation3d

# Assuming the snippet is in src/apriltag/multitag.py
from src.apriltag.multitag import multi_tag_pose

class TestMultiTagPose:
    """ Tests the SolvePnP wrapper for multi-tag robot localization. """

    # --- Fixtures ---

    @pytest.fixture
    def mock_camera(self):
        """ Creates a mock camera with standard calibration matrices. """
        cam = MagicMock()
        cam.calibration.camera_intrinsics = [
            [1000, 0, 640],
            [0, 1000, 360],
            [0, 0, 1]
        ]
        cam.calibration.camera_distortion = [0, 0, 0, 0, 0]
        return cam

    @pytest.fixture
    def mock_tag(self):
        """ Creates a mock AprilTag at a fixed world position. """
        tag = MagicMock()
        # Tag is at (5, 5, 0) in the world
        tag.global_pose = Pose3d(Translation3d(5, 5, 0), Rotation3d(0, 0, 0))
        # 2D corners on screen
        tag.corners = [100, 100, 200, 100, 200, 200, 100, 200]
        return tag

    # --- Tests ---

    @pytest.mark.parametrize("tags_list, expected_to_fail", [
        ([], True),                   # No tags at all
        ([MagicMock(global_pose=None)], True) # Tag exists but has no field position
    ], ids=["Empty Tag List", "Tag with No Global Pose"])
    def test_insufficient_data_returns_none(self, mock_camera, tags_list, expected_to_fail):
        """ Verify that if we don't have enough valid data, we return None safely. """
        pose, vecs = multi_tag_pose(tags_list, mock_camera)
        
        if expected_to_fail:
            assert pose is None
            assert vecs == (None, None)

    def test_solvepnp_success(self, mock_camera, mock_tag, monkeypatch):
        """
        Tests that multi_tag_pose correctly calls SolvePnP and returns a Pose2d.
        """
        # 1. Arrange: Create fake results for OpenCV to return
        fake_rvec = np.zeros((3, 1))
        fake_tvec = np.zeros((3, 1))
        
        # We use monkeypatch to replace cv2.solvePnP with a fake version for this test only
        mock_solve = MagicMock(return_value=(True, fake_rvec, fake_tvec))
        monkeypatch.setattr("src.apriltag.multitag.cv2.solvePnP", mock_solve)

        # 2. Act
        pose, (rvec, tvec) = multi_tag_pose([mock_tag], mock_camera)

        # 3. Assert
        assert pose is not None
        assert np.array_equal(rvec, fake_rvec)
        assert np.array_equal(tvec, fake_tvec)
        mock_solve.assert_called_once()

    def test_rejection_of_large_jumps(self, mock_camera, mock_tag, monkeypatch):
        """ 
        Tests the logic that rejects a new pose if it's too far (>= 0.5m) 
        from the previous estimate when only one tag is visible.
        """
        # 1. Arrange: 
        # Old position at origin
        old_rvec = np.zeros((3, 1))
        old_tvec = np.zeros((3, 1))

        # New position calculated by OpenCV is 10 meters away
        new_rvec = np.zeros((3, 1))
        new_tvec = np.array([[10.0], [0.0], [0.0]]) 

        mock_solve = MagicMock(return_value=(True, new_rvec, new_tvec))
        monkeypatch.setattr("src.apriltag.multitag.cv2.solvePnP", mock_solve)

        # 2. Act: Pass in the old vectors as an 'extrinsic guess'
        pose, (r, t) = multi_tag_pose([mock_tag], mock_camera, rvec=old_rvec, tvec=old_tvec)
        
        # 3. Assert: 
        # It should return None because 10m > 0.5m and we only have 1 tag (4 points)
        assert pose is None
        # It should return the original (old) vectors back to the caller
        assert np.array_equal(r, old_rvec)
        assert np.array_equal(t, old_tvec)
