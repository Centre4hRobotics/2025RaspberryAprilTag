""" Filter Apriltags """

from enum import Enum
import dataclasses

from src import apriltag

class ListType(Enum):
    """ Determine which type of List (blacklist or whitelist) is being used. """
    WHITELIST = 0
    BLACKLIST = 1

@dataclasses.dataclass
class FilterList:
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

    def filter_tags(self, tags: list[apriltag.Apriltag]) -> list[apriltag.Apriltag]:
        """ Remove filtered entries from a list. """

        if self.type is ListType.WHITELIST:
            return [
                tag for tag in tags
                if tag.id in self.list and tag.id <= 32
            ] # filter elements in blacklist

        return [
            tag for tag in tags
            if tag.id not in self.list and tag.id <= 32
        ] # filter elements in blacklist
