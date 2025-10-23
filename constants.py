""" Store stuff that is static """

import dataclasses
from enum import Enum

@dataclasses.dataclass
class Colors:
    """ Store the colors we use in one place """
    detection = (255, 255, 0)
    best_detection = (0, 255, 0)

colors = Colors()

class ListType(Enum):
    """ Determine which type of List (blacklist or whitelist) is being used. """
    WHITELIST = 0
    BLACKLIST = 1

class List:
    """ Keep blacklist/whitelist in one place """
    def __init__(self, config):

        if config["whitelist"] is not None and config["blacklist"] is not None:
            raise ValueError("Whitelist and Blacklist are both set!")

        if config["blacklist"] is not None:
            self.list = config["blacklist"]
            self.type = ListType.BLACKLIST

        elif config["whitelist"] is not None:
            self.list = config["whitelist"]
            self.type = ListType.WHITELIST

        else: # No blacklist or whitelist; allow all tags
            self.list = []
            self.type = ListType.BLACKLIST

    def verify_tags(self, og_tags):
        """ Remove filtered entries from a list. """
        if self.type is ListType.WHITELIST:
            tags = [t for t in og_tags if t.id in self.list] # remove elements not in the whitelist
        else: # If blacklist
            tags = [t for t in og_tags if t.id not in self.list] # remove elements in the blacklist
        return tags
