from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


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

    ids: list[str]
    slices: list[SliceElement]


@dataclass
class SliceResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    max_indices: list[int]


slice_route = Route(
    schema=load_schema(Path(__file__)),
    params=Slice,
    response=SliceResponse,
)

__all__ = ["Slice", "SliceElement", "SliceResponse", "slice_route"]
