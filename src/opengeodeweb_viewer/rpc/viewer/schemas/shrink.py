from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class Shrink(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    ids: list[str]
    shrink_factor: float


@dataclass
class ShrinkResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



shrink_route = Route(
    schema=load_schema(Path(__file__)),
    params=Shrink,
    response=ShrinkResponse,
)

__all__ = ["Shrink", "ShrinkResponse", "shrink_route"]
