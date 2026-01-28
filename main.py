""" This is the main file for FRC Team 4027's 2026 AprilTag Vision. """


from wpimath.geometry import Pose3d

from src import constants, settings
from src.apriltag import apriltag, multitag

def main() -> None:
    """ Main loop """

    init = settings.Settings("config/Constants.json")

    # Retained variables
    robot_pose = Pose3d()
    best_tag = None

    while True:

        # Reset local variables
        has_tag = False

        # Update selections
        cam_index: int = init.tables.camera_choice.get()
        cam = init.cameras[cam_index]
        cam.update()

        detections = init.estimators[cam_index].detector.detect(cam.get_frame()) # type: ignore

        tags = [apriltag.Apriltag(detection) for detection in detections]

        # Calculate global pose
        robot_pose = multitag.multi_tag_pose(tags, cam)

        # Change tags based on whitelist/blacklist
        tags = init.filter_list.filter_tags(tags)

        if tags: # If there are tags to look at
            has_tag = True

            # Draw & undistort tags
            for tag in tags:
                cam.mat = tag.draw_corners(cam.mat, constants.Colors.detection)

                tag.undistort_corners(cam.calibration)

                tag.calculate_pose(init.estimators[cam_index])

            # Get most centered tag
            tag_x_pos = [x.x_dist(cam.calibration.x_res) for x in tags]
            best_tag_index = tag_x_pos.index(min(tag_x_pos))

            best_tag = tags[best_tag_index]
            cam.mat = best_tag.draw_corners(cam.mat, constants.Colors.best_detection)

        # Publish everything to network tables

        init.output_stream.putFrame(cam.mat)

        init.tables.set_values(
            # General
            has_tag,
            robot_pose,
            # Centered Tag
            best_tag
        )

if __name__ == "__main__":
    main()
