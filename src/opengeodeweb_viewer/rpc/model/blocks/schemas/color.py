from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ColorClass(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    b: int
    g: int
    r: int
    a: Optional[float] = None


@dataclass
class Color(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    block_ids: List[int]
    color: ColorClass
    id: str
