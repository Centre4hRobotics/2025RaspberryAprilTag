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

@dataclasses.dataclass
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

def verify_tags(filter_list: List, og_tags):
    """ Remove filtered entries from a list. """
    if filter_list.type is ListType.WHITELIST:
        return [t for t in og_tags if t.id in filter_list.list] # remove elements not in whitelist
    return [t for t in og_tags if t.id not in filter_list.list] # remove elements in blacklist
