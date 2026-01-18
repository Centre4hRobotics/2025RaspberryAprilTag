""" Represent apriltags & allow operations on them """

import math

import numpy
import robotpy_apriltag
from wpimath.geometry import Rotation3d, Transform3d, CoordinateSystem, Pose3d, Pose2d, Translation2d, Rotation2d
import cv2

from src.camera import calibration

flip_tag_rotation = Rotation3d(axis = (0, 1, 0), angle = math.pi)
aprilTag_field_layout = robotpy_apriltag.AprilTagFieldLayout("config/TagPoses.json")


class Apriltag:
    """ Represent apriltag data """

    def __init__(self, detection: robotpy_apriltag.AprilTagDetection):

        self.detection = detection
        self.id = detection.getId()
        self.corners = list(self.detection.getCorners(tuple(numpy.empty(8).astype(float))))
        self.undistorted_corners = self.corners

        self.tag_to_camera = Transform3d()
        self.global_pose = aprilTag_field_layout.getTagPose(self.id)
        self.camera_pose = Pose3d()

    def draw_corners(self, mat, line_color):
        """ Draw the corners of this tag onto the screen """

        for i in range(4):
            j = (i + 1) % 4

            p1 = (int(self.corners[2 * i]),int(self.corners[2 * i + 1]))
            p2 = (int(self.corners[2 * j]),int(self.corners[2 * j + 1]))

            mat = cv2.line(mat, p1, p2, line_color, 2)

        return mat

    def undistort_corners(self, camera_calibration) -> None:
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

        for i in range(4):
            self.undistorted_corners[2 * i] = undistorted_corners[i][0][0]
            self.undistorted_corners[2 * i + 1] = undistorted_corners[i][0][1]

    def x_dist(self, x_res):
        """ Get the x-position (0 is the left side) """
        return (2 * self.detection.getCenter().x - x_res) / x_res

    def calculate_pose(self, estimator):
        """ Calculate the pose of the camera relative to the tag """

        cam_to_tag = estimator.pose_estimator.estimate(
            homography = self.detection.getHomography(),
            corners = tuple(self.undistorted_corners)
        )

        # Start by flipping the tag's rotation, to orient it as a viewer
        cam_to_tag = Transform3d(cam_to_tag.translation(),
                                    cam_to_tag.rotation().rotateBy(flip_tag_rotation))

        # Change coordinate system from East/Down/North to a WPILib standard North/West/Up
        cam_to_tag = CoordinateSystem.convert(cam_to_tag,
                                                    CoordinateSystem.EDN(),
                                                    CoordinateSystem.NWU())

        # Convert the transformation from camera->tag to tag->camera
        self.tag_to_camera = cam_to_tag.inverse()

        return self.tag_to_camera

def multi_tag_pose(tags: list[Apriltag], camera_calibration: calibration.CameraCalibration) -> Pose2d:
    """ Use SolvePNP to find the robot's pose. """

    # World Points (corners of tags)
    world_points = numpy.array([[t.global_pose.x, t.global_pose.y, t.global_pose.z] for t in tags if t.global_pose is not None])

    # Screen points (corners of tags)
    screen_points = numpy.array([[t.detection.getCenter().x, t.detection.getCenter().x] for t in tags if t.global_pose is not None])

    # Distortions
    distortion = numpy.array(camera_calibration.camera_distortion)

    # Intrinsics
    intrinsics = numpy.array(camera_calibration.camera_intrinsics)

    success, rvec, tvec = cv2.solvePnP(world_points, screen_points, intrinsics, distortion)

    if success:
        R, _ = cv2.Rodrigues(rvec)

        cam_pos_world = -R.T @ tvec

        x, y, _ = cam_pos_world.reshape(3)

        return Pose2d(Translation2d(float(x), float(y)), Rotation2d())

    return Pose2d()
