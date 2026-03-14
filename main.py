""" This is the main file for FRC Team 4027's 2026 AprilTag Vision. """

import json
import time

import cv2
import numpy

from src import apriltag, settings, debug

from cameras.picamera_capture import PiCamCapture

def main() -> None:
    """ Main loop """

    # Initialize code
    init = settings.Settings("config/Settings.json", [PiCamCapture()])
    print("initialized tables & stuff")
    # easier calling
    cam = init.cameras[0]
    estimator = init.estimators[0]

    # Retained variables
    best_tag = None

    # Save rvec and tvec from solvepnp calls
    rvec = None
    tvec = None

    # Debugging
    start_time = time.time()

    while True:

        # Update camera frame
        cam.update()

        detections = estimator.detector.detect(cam.get_frame()) # type: ignore

        tags = [apriltag.Apriltag(detection, init.field) for detection in detections]

        # Calculate global pose
        global_pose, (rvec, tvec) = apriltag.multi_tag_pose(tags, cam, rvec=rvec, tvec=tvec)

        # Change tags based on whitelist/blacklist
        tags = init.filter_list.filter_tags(tags)

        if tags != []: # If there are tags to look at

            # Get most centered tag
            tag_x_pos = [abs(tag.x_dist(cam.calibration.x_res)) for tag in tags]
            best_tag_index = tag_x_pos.index(min(tag_x_pos))

            best_tag = tags[best_tag_index]
            best_tag.draw_corners(cam.mat, (0, 255, 0))

            # Draw & undistort tags
            for tag in tags:
                if tag != best_tag:
                    tag.draw_corners(cam.mat, (255, 255, 0))

                tag.undistort_corners(cam.calibration)

                tag.calculate_pose(estimator)

        # Crosshair
        cv2.line(
            cam.mat,
            (int( 10 + cam.calibration.x_res/2), int( 10 + cam.calibration.y_res/2)),
            (int(-10 + cam.calibration.x_res/2), int(-10 + cam.calibration.y_res/2)),
            (255, 0, 0), 2
        )
        cv2.line(
            cam.mat,
            (int( 10 + cam.calibration.x_res/2), int(-10 + cam.calibration.y_res/2)),
            (int(-10 + cam.calibration.x_res/2), int( 10 + cam.calibration.y_res/2)),
            (255, 0, 0), 2
        )

        # Publish everything to network tables

        runtime = time.time() - start_time
        if global_pose is not None:
            debug.add_data(runtime, global_pose.translation().y, 1)
            debug.add_data(runtime, len(tags), 2)
        else:
            debug.add_data(runtime, numpy.nan, 1)
            debug.add_data(runtime, numpy.nan, 2)

        cam.rotate_mat()
        cam.output_stream.putFrame(cam.mat)

        init.tables.set_values(
            # General
            tags,
            global_pose,
            # Centered Tag
            best_tag
        )

if __name__ == "__main__":

    with open('config/Settings.json', 'r', encoding='utf-8') as file:
        js = json.load(file)

    if js['debug']:
        debug.create_plot('Time', 'TTC Y (m)', 'Best Tag')

        try:
            main()
        except KeyboardInterrupt:
            debug.save_plot('error.png')
    else:
        try:
            main()
        except KeyboardInterrupt:
            pass
