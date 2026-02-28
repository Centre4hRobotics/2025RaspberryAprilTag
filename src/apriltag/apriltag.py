""" Represent apriltags & allow operations on them """

import math

import numpy
import robotpy_apriltag
from wpimath.geometry import Rotation3d, Transform3d, CoordinateSystem
import cv2

from src import camera, apriltag

flip_tag_rotation = Rotation3d(axis = (0, 1, 0), angle = math.pi)

class Apriltag:
    """ Represent apriltag data """

    def __init__(self, detection: robotpy_apriltag.AprilTagDetection, field: robotpy_apriltag.AprilTagFieldLayout):

        self.detection = detection
        self.id = detection.getId()
        self.corners = self.detection.getCorners(tuple(numpy.empty(8).astype(float)))
        self.undistorted_corners = self.corners

        self.tag_to_camera = Transform3d()
        self.global_pose = field.getTagPose(self.id)

    def __ne__(self, other) -> bool:
        return self.id != other.id

    def __lt__(self, other) -> bool:
        return self.id < other.id

    def draw_corners(self, mat: cv2.typing.MatLike, line_color: tuple[int, int, int]) -> None:
        """ Draw the corners of this tag onto the screen """

        for i in range(4):
            j = (i + 1) % 4

            p1 = (int(self.corners[2 * i]),int(self.corners[2 * i + 1]))
            p2 = (int(self.corners[2 * j]),int(self.corners[2 * j + 1]))

            mat = cv2.line(mat, p1, p2, line_color, 2)

    def undistort_corners(self, camera_calibration: camera.calibration.CameraCalibration) -> None:
        """ Undistort the corners of the apriltag (nessecary for accurate pose estimation) """

        distorted_corners = numpy.empty([4,2], dtype=numpy.float32)
        for i in range(4):
            distorted_corners[i][0] = self.corners[2 * i]
            distorted_corners[i][1] = self.corners[2 * i + 1]

        # run the OpenCV undistortion routine to fix the corners
        undistorted_corners = cv2.undistortImagePoints(
            distorted_corners,
            camera_calibration.camera_intrinsics,
            camera_calibration.camera_distortion
        )

        # Flatten
        self.undistorted_corners: tuple[float, float, float, float, float, float, float, float] = (
            undistorted_corners[0][0][0], undistorted_corners[0][0][1],
            undistorted_corners[1][0][0], undistorted_corners[1][0][1],
            undistorted_corners[2][0][0], undistorted_corners[2][0][1],
            undistorted_corners[3][0][0], undistorted_corners[3][0][1]
        )

    def x_dist(self, x_res: int) -> float:
        """ Get the x-position (0 is the left side, 1 is the right) """
        return (2 * self.detection.getCenter().x - x_res) / x_res

    def calculate_pose(self, estimator: apriltag.apriltag_estimator.ApriltagEstimator) -> Transform3d:
        """ Calculate the pose of the camera relative to the tag """

        cam_to_tag = estimator.pose_estimator.estimate(
            homography = self.detection.getHomography(),
            corners = self.undistorted_corners
        )

        # Start by flipping the tag's rotation, to orient it as a viewer
        cam_to_tag = Transform3d(
            cam_to_tag.translation(),
            cam_to_tag.rotation().rotateBy(flip_tag_rotation)
        )

        # Change coordinate system from East/Down/North to a WPILib standard North/West/Up
        cam_to_tag = CoordinateSystem.convert(cam_to_tag,
            CoordinateSystem.EDN(),
            CoordinateSystem.NWU()
        )

        # Convert the transformation from camera->tag to tag->camera
        self.tag_to_camera = cam_to_tag.inverse()

        return self.tag_to_camera
