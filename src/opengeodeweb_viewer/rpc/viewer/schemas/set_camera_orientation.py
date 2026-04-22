from dataclasses_json import DataClassJsonMixin
from enum import Enum
from dataclasses import dataclass


class Direction(Enum):
    BOTTOM = "bottom"
    EAST = "east"
    NORTH = "north"
    SOUTH = "south"
    TOP = "top"
    WEST = "west"


@dataclass
class SetCameraOrientation(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    direction: Direction
