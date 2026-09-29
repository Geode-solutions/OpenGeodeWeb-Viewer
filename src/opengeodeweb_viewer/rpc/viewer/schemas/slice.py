from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List


@dataclass
class SliceElement(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    axis: int
    index: int


@dataclass
class Slice(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    ids: List[str]
    slices: List[SliceElement]
