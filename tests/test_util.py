""" Test the various utilities we use """

import math

import pytest
from wpimath.geometry import Pose3d, Translation3d, Rotation3d

from src import geometry

class TestUtils:
    """ Test the various wrappers and fixtures """

    @pytest.mark.parametrize(
        "pose, expected, from_, to",
        [
            (Pose3d(), Pose3d(), geometry.CoordinateSystem.NWU, geometry.CoordinateSystem.EDN),
            (Pose3d(Translation3d(), Rotation3d(0, 0, math.pi)), Pose3d(Translation3d(), Rotation3d(0, math.pi, 0)), geometry.CoordinateSystem.NWU, geometry.CoordinateSystem.EDN),
            (Pose3d(Translation3d(1, 0, 0), Rotation3d()), Pose3d(Translation3d(0, 0, 1), Rotation3d()), geometry.CoordinateSystem.NWU, geometry.CoordinateSystem.EDN),
            (Pose3d(Translation3d(1, -1, 0), Rotation3d()), Pose3d(Translation3d(1, 0, 1), Rotation3d()), geometry.CoordinateSystem.NWU, geometry.CoordinateSystem.EDN)
        ]
    )
    def test_coordinate_system(self, pose, expected, from_, to):
        """ Ensure that the coordinate system conversions actually work """
        converted = geometry.convert_pose3d(pose, from_, to)
        assert converted == expected
        # make sure it's reversible
        original = geometry.convert_pose3d(converted, to, from_)
        assert original == pose

    @pytest.mark.parametrize(
        "tag_pose",
        [
            Pose3d(Translation3d(1, 0, 0), Rotation3d(0, 0, math.pi))
        ]
    )
    def test_tag_corners(self, mock_tag, tag_pose):
        """ Ensure tag corners are within camera FOV """
        tag = mock_tag(tag_pose, Pose3d())

        assert 0 <= tag.corners[0] <= 1280
        assert 0 <= tag.corners[1] <= 800
        assert 0 <= tag.corners[2] <= 1280
        assert 0 <= tag.corners[3] <= 800
        assert 0 <= tag.corners[4] <= 1280
        assert 0 <= tag.corners[5] <= 800
        assert 0 <= tag.corners[6] <= 1280
        assert 0 <= tag.corners[7] <= 800
