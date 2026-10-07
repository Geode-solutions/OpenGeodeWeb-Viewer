from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class Visibility(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    block_ids: list[int]
    id: str
    visibility: bool


@dataclass
class VisibilityResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



visibility_route = Route(
    schema=load_schema(Path(__file__)),
    params=Visibility,
    response=VisibilityResponse,
)

__all__ = ["Visibility", "VisibilityResponse", "visibility_route"]
