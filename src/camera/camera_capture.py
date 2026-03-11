""" Abstract class for camera captures """

import abc

import cv2

class CaptureBase(abc.ABC):
    """ Define a base class for camera captures """

    @abc.abstractmethod
    def set_profile(self, profile: dict) -> None:
        """ Set camera profile """

    @abc.abstractmethod
    def get_frame(self) -> cv2.typing.MatLike:
        """ Get frame from camera """
