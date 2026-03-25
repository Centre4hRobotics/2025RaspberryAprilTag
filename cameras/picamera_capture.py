""" Implement picamera2 camera """

import os

import picamera2
import cv2

from src.camera.capture import CaptureBase

# Quiet picamera2's logging to errors only
os.environ["LIBCAMERA_LOG_LEVELS"] = "4"

class PiCamCapture(CaptureBase):
    """ Implement Picamera2 for camera captures (required for Luma P1) """
    def __init__(self):
        self.capture = picamera2.Picamera2()

    def set_profile(self, profile: dict) -> None:
        camera_config = self.capture.create_video_configuration(
            main={
                'size': (profile['resolution']['x'], profile['resolution']['y'])
            }
        )

        self.capture.configure(camera_config)
        self.capture.start()

    def get_frame(self) -> cv2.typing.MatLike:
        return self.capture.capture_array()
