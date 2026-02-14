""" This is the main file for FRC Team 4027's 2026 AprilTag Vision. """

import time

from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
import cv2
import numpy

from src import settings
from src.apriltag import apriltag, multitag

def main() -> None:
    """ Main loop """

    init = settings.Settings("config/Settings.json")

    cam = init.camera

    # Retained variables
    robot_pose = None
    best_tag = None

    rvec = None
    tvec = None

    error_data = []
    tag_count = []
    start = time.time()
    runtime = 0

    while runtime < 20:

        runtime = time.time() - start
        print(runtime)

        # Reset local variables
        has_tag = False

        # Update selections
        cam.update()

        detections = init.estimator.detector.detect(cam.get_frame()) # type: ignore

        tags = [apriltag.Apriltag(detection) for detection in detections]

        # Calculate global pose
        robot_pose, rvec, tvec = multitag.multi_tag_pose(tags, cam, rvec, tvec)

        # Change tags based on whitelist/blacklist
        tags = init.filter_list.filter_tags(tags)

        if tags: # If there are tags to look at
            has_tag = True

            # Draw & undistort tags
            for tag in tags:
                cam.mat = tag.draw_corners(cam.mat, (255, 255, 0))

                tag.undistort_corners(cam.calibration)

                tag.calculate_pose(init.estimator)

            # Get most centered tag
            tag_x_pos = [abs(x.x_dist(cam.calibration.x_res)) for x in tags]
            best_tag_index = tag_x_pos.index(min(tag_x_pos))

            best_tag = tags[best_tag_index]
            cam.mat = best_tag.draw_corners(cam.mat, (0, 255, 0))

        # Crosshair
        cam.mat = cv2.line(
            cam.mat,
            (int( 10 + cam.calibration.x_res/2), int( 10 + cam.calibration.y_res/2)),
            (int(-10 + cam.calibration.x_res/2), int(-10 + cam.calibration.y_res/2)),
            (255, 0, 0), 2
        )
        cam.mat = cv2.line(
            cam.mat,
            (int( 10 + cam.calibration.x_res/2), int(-10 + cam.calibration.y_res/2)),
            (int(-10 + cam.calibration.x_res/2), int( 10 + cam.calibration.y_res/2)),
            (255, 0, 0), 2
        )


        if robot_pose is not None and best_tag is not None and best_tag.global_pose is not None:
            error = robot_pose.y
            error_data.append((runtime, error))
            if len(tags) == 1:
                tag_count.append((runtime, (best_tag.id - 25) + .5))
                # 25 -> 1/2
                # 26 -> 3/2
            else:
                tag_count.append((runtime, len(tags)))
        else:
            error_data.append((runtime, numpy.nan))
            tag_count.append((runtime, 0))


        # Publish everything to network tables

        cam.output_stream.putFrame(cam.mat)

        init.tables.set_values(
            # General
            has_tag,
            robot_pose,
            # Centered Tag
            best_tag
        )

    # WARNING: ChatGPT used ahead (for matplotlib stuff)

    x1, y1 = zip(*error_data)
    x2, y2 = zip(*tag_count)

    fig, ax1 = plt.subplots()

    ax1.plot(x1, y1)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Position (m)')

    ax2 = ax1.twinx()

    ax2.plot(x2, y2, color='orange')
    ax2.set_ylabel('Best Tag')
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

    fig.savefig("error.png")

if __name__ == "__main__":
    main()
