""" Implement picamera2 camera """

import picamera2
import cv2

from camera_capture import CaptureBase

class PiCamCapture(CaptureBase):
    def __init__(self, profile: dict):
        self.capture = picamera2.Picamera2()

        camera_config = self.capture.create_video_configuration(
            main={
                'size': (profile['x'], profile['y'])
            }
        )

        self.capture.configure(camera_config)
        self.capture.start()

    def get_frame(self) -> cv2.typing.MatLike:
        return self.capture.capture_array()
