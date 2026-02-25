""" Abstract class for camera captures """

import abc

import cv2

class CaptureBase(abc.ABC):
    @abc.abstractmethod
    def __init__(self, profile: dict):
        pass

    @abc.abstractmethod
    def get_frame(self) -> cv2.typing.MatLike:
        pass
