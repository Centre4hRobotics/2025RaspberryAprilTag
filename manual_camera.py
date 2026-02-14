""" Take images, using network tables for preview """

import threading
import time
from pathlib import Path

import cv2

from src import settings

def take_images(init: settings.Settings, camera_lock: threading.Lock):
    """ Take CLI input to take photos """
    while True:

        # Wait for input
        _ = input("[Take Image]")
        print("took photo")

        with camera_lock:
            image = init.camera.get_frame()

        file_name = Path('calibration/0_img.png')

        # Determine correct file name
        while file_name.is_file():
            num = int(file_name.stem[:-4]) + 1
            file_name = Path('calibration/' + str(num) + '_img.png')

        cv2.imwrite(file_name, image)

def main() -> None:
    """ Activate the thread """

    camera_lock = threading.Lock()

    init = settings.Settings("config/Settings.json")

    input_thread = threading.Thread(target=take_images, args=(init, camera_lock), daemon=True)
    input_thread.start()

    while True:
        with camera_lock:
            init.camera.update()
            image = init.camera.get_frame()

        init.camera.output_stream.putFrame(image)

        time.sleep(1/30)

if __name__ == '__main__':
    main()
