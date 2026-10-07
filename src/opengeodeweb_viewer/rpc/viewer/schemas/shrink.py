from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import List


@dataclass
class Shrink(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    ids: List[str]
    shrink_factor: float


@dataclass
class ShrinkResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


shrink_route = Route(
    schema=load_schema(Path(__file__)),
    params=Shrink,
    response=ShrinkResponse,
)

__all__ = ["Shrink", "ShrinkResponse", "shrink_route"]
