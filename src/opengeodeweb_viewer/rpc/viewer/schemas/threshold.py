from dataclasses_json import DataClassJsonMixin
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class Location(Enum):
    CELL = "cell"
    POINT = "point"


@dataclass
class Attribute(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    item: int
    location: Location
    maximum: float
    minimum: float
    name: str


@dataclass
class Threshold(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    ids: List[str]
    attribute: Optional[Attribute] = None
