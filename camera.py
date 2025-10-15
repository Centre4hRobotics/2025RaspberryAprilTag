from cscore import CameraServer

class Camera:
    """ Wrap cameras """
    def __init__(self, num, calibration):
        self.cam = CameraServer.startAutomaticCapture(num)

        self.cam.setResolution(calibration.x_res, calibration.y_res)

        self.cv_sink = CameraServer.getVideo(self.cam)
