from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


@dataclass
class ColorClass(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

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
