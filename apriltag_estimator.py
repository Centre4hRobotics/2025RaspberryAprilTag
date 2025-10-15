""" Wrap the WPILib apriltag stuff """

import robotpy_apriltag

class ApriltagEstimator:
    """ its a one-class file, c\'mon... """
    def __init__(self, calibration):

        pose_estimator_config = robotpy_apriltag.AprilTagPoseEstimator.Config(
            0.1651,  #tag size in meters
            calibration.Fx,
            calibration.Fy,
            calibration.Cx,
            calibration.Cy,
        )

        self.pose_estimator = robotpy_apriltag.AprilTagPoseEstimator(pose_estimator_config)

        self.apriltag_detector = robotpy_apriltag.AprilTagDetector()
        self.apriltag_detector.addFamily("tag36h11", 3)

        self.apriltag_detector_config = self.apriltag_detector.getConfig()
        self.apriltag_detector_config.numThreads = 4
        self.apriltag_detector_config.quadSigma = 0.5
        self.apriltag_detector_config.quadDecimate = 1
        self.apriltag_detector.setConfig(self.apriltag_detector_config)

        self.quad_threshold_parameters = self.apriltag_detector.getQuadThresholdParameters()
        self.quad_threshold_parameters.minClusterPixels = 5
        self.quad_threshold_parameters.criticalAngle = 0.79
        self.apriltag_detector.setQuadThresholdParameters(self.quad_threshold_parameters)
