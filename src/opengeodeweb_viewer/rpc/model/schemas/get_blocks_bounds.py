from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class GetBlocksBounds(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    block_ids: list[int]
    id: str


@dataclass
class GetBlocksBoundsResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    bounds: list[float]


get_blocks_bounds_route = Route(
    schema=load_schema(Path(__file__)),
    params=GetBlocksBounds,
    response=GetBlocksBoundsResponse,
)

__all__ = ["GetBlocksBounds", "GetBlocksBoundsResponse", "get_blocks_bounds_route"]
