""" Wrap the WPILib apriltag stuff """

import dataclasses
import robotpy_apriltag

@dataclasses.dataclass
class ApriltagEstimator:
    """ its a one-class file, c\'mon... """
    def __init__(self, calibration):

        pose_estimator_config = robotpy_apriltag.AprilTagPoseEstimator.Config(
            0.1651,  #tag size in meters
            calibration.camera_intrinsics[0][0],
            calibration.camera_intrinsics[1][1],
            calibration.camera_intrinsics[0][2],
            calibration.camera_intrinsics[1][2],
        )

        self.pose_estimator = robotpy_apriltag.AprilTagPoseEstimator(pose_estimator_config)

        self.apriltag_detector = robotpy_apriltag.AprilTagDetector()
        self.apriltag_detector.addFamily("tag36h11", 3)

        apriltag_detector_config = self.apriltag_detector.getConfig()
        apriltag_detector_config.numThreads = 4
        apriltag_detector_config.quadSigma = 0.5
        apriltag_detector_config.quadDecimate = 1
        self.apriltag_detector.setConfig(apriltag_detector_config)

        quad_threshold_parameters = self.apriltag_detector.getQuadThresholdParameters()
        quad_threshold_parameters.minClusterPixels = 5
        quad_threshold_parameters.criticalAngle = 0.79
        self.apriltag_detector.setQuadThresholdParameters(quad_threshold_parameters)
