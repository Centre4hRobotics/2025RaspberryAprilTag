""" This is the main file for FRC Team 4027's 2026 AprilTag Vision. """

import time

import cv2
import numpy

from src import settings
from src.apriltag import apriltag, multitag
from src.debug import Plot


def main() -> None:
    """ Main loop """

    plot = Plot('Time', 'TTC y (m)', 'Best Tag')

    try:
        # Initialize code
        init = settings.Settings("config/Settings.json")

        # easier calling
        cam = init.camera

        # Retained variables
        robot_pose = None
        best_tag = None

        # Save rvec and tvec from solvepnp calls
        rvec = None
        tvec = None

        # Debugging
        start_time = time.time()

        while True:

            # Declare local variable
            has_tag = False

            # Update camera frame
            cam.update()

            detections = init.estimator.detector.detect(cam.get_frame()) # type: ignore

            tags = [apriltag.Apriltag(detection, init.field) for detection in detections]

            # Calculate global pose
            robot_pose, (rvec, tvec) = multitag.multi_tag_pose(tags, cam, rvec=rvec, tvec=tvec)

            # Change tags based on whitelist/blacklist
            tags = init.filter_list.filter_tags(tags)

            if tags: # If there are tags to look at
                has_tag = True

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

                    tag.calculate_pose(init.estimator)

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
            if best_tag:
                plot.add_data(runtime, best_tag.tag_to_camera.y, 1)
                plot.add_data(runtime, best_tag.id, 2)
            else:
                plot.add_data(runtime, numpy.nan, 1)
                plot.add_data(runtime, numpy.nan, 2)


            cam.rotate_mat()
            cam.output_stream.putFrame(cam.mat)

            init.tables.set_values(
                # General
                has_tag,
                robot_pose,
                # Centered Tag
                best_tag
            )
    except KeyboardInterrupt:
        plot.save_plot('error.png')

if __name__ == "__main__":
    main()
