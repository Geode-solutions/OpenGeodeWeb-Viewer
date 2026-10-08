from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import List


@dataclass
class GetBlocksBounds(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    block_ids: List[int]
    id: str


@dataclass
class GetBlocksBoundsResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    bounds: List[float]


get_blocks_bounds_route = Route(
    schema=load_schema(Path(__file__)),
    params=GetBlocksBounds,
    response=GetBlocksBoundsResponse,
)

__all__ = ["GetBlocksBounds", "GetBlocksBoundsResponse", "get_blocks_bounds_route"]
