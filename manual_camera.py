""" Take images, using network tables for preview """

import threading
import time
from pathlib import Path

import cv2
from cscore import CameraServer

from src import camera
from cameras.picamera_capture import PiCamCapture

def take_images(cam: camera.camera_capture.CaptureBase, camera_lock: threading.Lock):
    """ Take CLI input to take photos """
    while True:

        # Wait for input
        _ = input("[Take Image]")
        print("took photo")

        with camera_lock:
            image = cam.get_frame()

        file_name = Path('calibration/0_img.png')

        # Determine correct file name
        while file_name.is_file():
            num = int(file_name.stem[:-4]) + 1
            file_name = Path('calibration/' + str(num) + '_img.png')

        cv2.imwrite(file_name, image)

def main() -> None:
    """ Activate the thread """

    camera_lock = threading.Lock()

    cam = PiCamCapture()

    input_thread = threading.Thread(target=take_images, args=(cam, camera_lock), daemon=True)
    input_thread.start()

    x_size, y_size, _ = cam.get_frame().shape

    output_stream = CameraServer.putVideo('Vision', x_size, y_size)

    while True:
        with camera_lock:
            image = cam.get_frame()

        output_stream.putFrame(image)

        time.sleep(1/30)

if __name__ == '__main__':
    main()
