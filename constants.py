""" Store stuff that is static """

import dataclasses
from enum import Enum

@dataclasses.dataclass
class Colors:
    """ Store the colors we use in one place """
    detection = (255, 255, 0)
    best_detection = (0, 255, 0)

class ListType(Enum):
    """"""
    WHITELIST = 0
    BLACKLIST = 1