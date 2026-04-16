from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import Optional, TypedDict, List
from enum import Enum


@dataclass
class ColorClass(DataClassJsonMixin):
    b: int
    g: int
    r: int
    a: Optional[float] = None


class ColorMode(Enum):
    CONSTANT = "constant"
    RANDOM = "random"


@dataclass
class Color(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    block_ids: List[int]
    color_mode: ColorMode
    id: str
    color: Optional[ColorClass] = None


class ColorRGB(TypedDict):
    r: int
    g: int
    b: int


class ColorResult(TypedDict):
    viewer_id: int
    geode_id: str
    color: ColorRGB
