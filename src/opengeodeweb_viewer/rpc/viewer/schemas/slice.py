from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import List


@dataclass
class SliceElement(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    axis: int
    index: int


@dataclass
class Slice(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    ids: List[str]
    slices: List[SliceElement]
