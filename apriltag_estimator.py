""" Wrap the WPILib apriltag estimation classes """

import dataclasses
import robotpy_apriltag

@dataclasses.dataclass
class ApriltagEstimator:
    """ Wrap WPILib apriltag pose estimator """
    def __init__(self, calibration):

        pose_estimator_config = robotpy_apriltag.AprilTagPoseEstimator.Config(
            0.1651,  #tag size in meters
            calibration.camera_intrinsics[0][0],
            calibration.camera_intrinsics[1][1],
            calibration.camera_intrinsics[0][2],
            calibration.camera_intrinsics[1][2],
        )

        self.pose_estimator = robotpy_apriltag.AprilTagPoseEstimator(pose_estimator_config)

        self.detector = robotpy_apriltag.AprilTagDetector()
        self.detector.addFamily("tag36h11", 3)

        apriltag_detector_config = self.detector.getConfig()
        apriltag_detector_config.numThreads = 4
        apriltag_detector_config.quadSigma = 0.5
        apriltag_detector_config.quadDecimate = 1
        self.detector.setConfig(apriltag_detector_config)

        quad_threshold_parameters = self.detector.getQuadThresholdParameters()
        quad_threshold_parameters.minClusterPixels = 5
        quad_threshold_parameters.criticalAngle = 0.79
        self.detector.setQuadThresholdParameters(quad_threshold_parameters)
