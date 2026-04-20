from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


@dataclass
class ColorClass(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    a: float
    b: int
    g: int
    r: int


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
