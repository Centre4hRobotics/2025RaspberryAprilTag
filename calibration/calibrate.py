""" Find camera intrinsics & distortions using OpenCV & ChArUco boards """

from glob import glob
import json

import cv2
from cv2 import aruco
import numpy

def generate_board(to_file: bool = False) -> aruco.CharucoBoard:
    """ Generate the ChArUco board we're using """

    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

    rows = 8 # vertical count
    columns = 8 # horizontal count
    square_size = 2.54 / 100 # size of square in meters
    marker_size = 0.75 * 2.54 / 100 # size of marker in meters

    board = aruco.CharucoBoard((columns, rows), square_size, marker_size, dictionary)

    if to_file:
        img = board.generateImage((1000, 700))
        cv2.imwrite('calibration/charuco_board.png', img)

    return board

def calibrate(board: aruco.CharucoBoard) -> tuple:
    """ Get the files & calibrate the camera """

    all_corners = []
    all_ids = []
    image_size = None
    detector = aruco.CharucoDetector(board)

    images = glob('*_img.png')

    for filename in images:
        img = cv2.imread(filename)

        if img is None:
            continue

        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if image_size is None:
            image_size = gray_img.shape[::-1]

        corners, ids, _, _ = detector.detectBoard(gray_img)

        if ids is not None and len(ids) > 3:
            all_corners.append(corners)
            all_ids.append(ids)

    ret, matrix, coeffs, _, _ = cv2.aruco.calibrateCameraCharuco(all_corners, all_ids, board, image_size, None, None)

    return ret, matrix, coeffs, image_size

def main() -> None:
    """ Tie it all together """

    board = generate_board()
    worked, matrix, coeffs, size = calibrate(board)

    print(f"Worked?: {bool(worked)}")
    print("Camera Matrix:")
    print(matrix)
    print(f"Distortion Coeffs: {coeffs}")

    json_data = {
        "GeneratedProfile": {
            "resolution": {
                "x": int(size[0]),
                "y": int(size[1])
            },
            "intrinsics": {
                "Fx": float(matrix[0, 0]),
                "Fy": float(matrix[0, 2]),
                "Cx": float(matrix[1, 1]),
                "Cy": float(matrix[1, 2])
            },
            "distortion": coeffs.tolist()[0],
        }
    }

    with open('generated_profile.json', 'w', encoding='utf-8') as file:
        json.dump(json_data, file, indent=4)

if __name__ == '__main__':
    main()
