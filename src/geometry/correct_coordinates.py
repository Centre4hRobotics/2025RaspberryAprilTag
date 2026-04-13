""" WPILib's CoordinateSystem is broken, we're fixing it """

from enum import Enum

import numpy
from wpimath.geometry import Translation3d, Rotation3d, Pose3d, Transform3d

class CoordinateSystem(Enum):
    """ Which coordinate system to use. OpenCV should use EDN, everything else uses NWU. """
    NWU = 0
    EDN = 1

def convert_translation3d(translation: Translation3d, from_: CoordinateSystem, to: CoordinateSystem):
    """ Convert a Translation3d """

    if from_ == CoordinateSystem.NWU and to == CoordinateSystem.EDN:
        return Translation3d(-translation.Y(), -translation.Z(), translation.X())
    elif from_ == CoordinateSystem.EDN and to == CoordinateSystem.NWU:
        return Translation3d(translation.Z(), -translation.X(), -translation.Y())
    return translation

R = numpy.array([
    [0, -1, 0],
    [0, 0, -1],
    [1, 0, 0]
], dtype=numpy.float32)

R_INV = R.T

def convert_rotation3d(rotation: Rotation3d, from_: CoordinateSystem, to: CoordinateSystem):
    """ Convert a Rotation3d """

    q = rotation.toMatrix()

    if from_ == CoordinateSystem.NWU and to == CoordinateSystem.EDN:
        return Rotation3d(R @ q @ R_INV)

    elif from_ == CoordinateSystem.EDN and to == CoordinateSystem.NWU:
        return Rotation3d(R_INV @ q @ R)

    else:
        return rotation

def convert_pose3d(pose: Pose3d, from_: CoordinateSystem, to: CoordinateSystem):
    """ Convert pose3d between coordinate systems """
    return Pose3d(convert_translation3d(pose.translation(), from_, to), convert_rotation3d(pose.rotation(), from_, to))

def convert_transform3d(transform: Transform3d, from_: CoordinateSystem, to: CoordinateSystem):
    """ Convert Transform3d """
    return Transform3d(convert_translation3d(transform.translation(), from_, to), convert_rotation3d(transform.rotation(), from_, to))
