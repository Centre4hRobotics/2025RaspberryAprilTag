""" Tests Multi-Tag Pose Computation with SolvePnP """

import math

import pytest
from wpimath.geometry import Pose3d, Rotation3d, Translation3d

from src.apriltag.multitag import multi_tag_pose

class TestMultiTagPose:
    """ Tests the SolvePnP wrapper for multi-tag robot localization. """

    # --- Tests ---

    @pytest.mark.parametrize(
        "camera_pose, tag_pose",
        [
            (Pose3d(), Pose3d(Translation3d(2, 0, 0), Rotation3d(0, 0, math.pi))),
            (Pose3d(), Pose3d(Translation3d(2, 1, 0), Rotation3d(0, 0, math.pi))),
            (Pose3d(), Pose3d(Translation3d(2, 1, 1), Rotation3d(0, 0, math.pi))),
            (Pose3d(), Pose3d(Translation3d(1, 0, 0), Rotation3d(0, 0, math.pi)))
        ]
    )
    def test_solvepnp_one(self, mock_camera, mock_tag, camera_pose, tag_pose):
        """ Make sure solvePnP calculates the right position """

        tag = mock_tag(tag_pose, camera_pose)

        pose, _ = multi_tag_pose([tag], mock_camera, None, None)

        assert pose.X() == pytest.approx(camera_pose.X(), abs=0.05)
        assert pose.Y() == pytest.approx(camera_pose.Y(), abs=0.05)
        assert pose.rotation().radians() == pytest.approx(camera_pose.rotation().Z(), abs=0.05)

    @pytest.mark.parametrize(
        "camera_pose, tag_poses",
        [
            (
                Pose3d(),
                [
                    Pose3d(Translation3d(1, 1, 0), Rotation3d(0, 0, math.pi)),
                    Pose3d(Translation3d(1, -1, 0), Rotation3d(0, 0, math.pi))
                ]
            )
        ]
    )
    def test_solvepnp_many(self, mock_camera, mock_tag, camera_pose, tag_poses):
        """ Ensure that we get the correct pose from multiple tags """

        tags = [mock_tag(pose, camera_pose, 0) for pose in tag_poses]

        pose, _ = multi_tag_pose(tags, mock_camera, None, None)

        assert pose.X() == pytest.approx(camera_pose.X(), abs=0.05)
        assert pose.Y() == pytest.approx(camera_pose.Y(), abs=0.05)
        assert pose.rotation().radians() == pytest.approx(camera_pose.rotation().Z(), abs=0.05)

    @pytest.mark.parametrize(
        "good_pose, bad_pose, tag_pose, expected",
        [
            (Pose3d(), Pose3d(Translation3d(-5, 0, 0), Rotation3d()), Pose3d(Translation3d(2, 0, 0), Rotation3d(0, 0, math.pi)), False),
            (Pose3d(), Pose3d(), Pose3d(Translation3d(2, 0, 0), Rotation3d(0, 0, math.pi)), True)
        ]
    )
    def test_rejection_of_jumps(self, mock_camera, mock_tag, good_pose, bad_pose, tag_pose, expected):
        """ Ensure that multi_tag_pose rejects major jumps in tag positions """

        tag = mock_tag(tag_pose, good_pose)

        pose, (rvec, tvec) = multi_tag_pose([tag], mock_camera, None, None)

        assert pose is not None

        tag = mock_tag(tag_pose, bad_pose)

        pose, (rvec, tvec) = multi_tag_pose([tag], mock_camera, rvec=rvec, tvec=tvec)

        assert (pose is not None) if expected else (pose is None)
