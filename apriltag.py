""" Represent apriltag data """

import numpy
import cv2

class Apriltag:
    """ Represent apriltag data """
    def __init__(self, detection):
        self.detection = detection
        self.id = detection.getId()
        self.corners = list(self.detection.getCorners(numpy.empty(8)))
        self.undistorted_corners = self.corners

    def draw_corners(self, mat, line_color):
        """ Draw the corners of this tag onto the screen """
        for i in range(4):
            j = (i + 1) % 4
            p1 = (int(self.corners[2 * i]),int(self.corners[2 * i + 1]))
            p2 = (int(self.corners[2 * j]),int(self.corners[2 * j + 1]))
            mat = cv2.line(mat, p1, p2, line_color, 2)

    def undistort_corners(self, calibration):
        """ Undistort the corners of the apriltag (nessecary for accurate pose estimation) """
        distorted_corners = numpy.empty([4,2], dtype=numpy.float32)
        for i in range(4):
            distorted_corners[i][0] = self.corners[2 * i]
            distorted_corners[i][1] = self.corners[2 * i + 1]

        # run the OpenCV undistortion routine to fix the corners
        undistorted_corners = cv2.undistortImagePoints(distorted_corners,
                                                       calibration.camera_intrinsics,
                                                       calibration.camera_distortion)

        for i in range(4):
            self.undistorted_corners[2 * i] = undistorted_corners[i][0][0]
            self.undistorted_corners[2 * i + 1] = undistorted_corners[i][0][1]

    def x_dist(self, x_res):
        return (2 * self.detection.getCenter().x - x_res) / x_res