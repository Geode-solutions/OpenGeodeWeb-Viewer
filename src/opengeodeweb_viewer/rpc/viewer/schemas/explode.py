from opengeodeweb_microservice.schema_types import DataId
from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import List


@dataclass
class Explode(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    explode_factor: float
    ids: List[DataId]


@dataclass
class ExplodedBounds(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    bounds: List[float]
    id: DataId


@dataclass
class ExplodeResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    exploded_bounds: List[ExplodedBounds]


explode_route = Route(
    schema=load_schema(Path(__file__)),
    params=Explode,
    response=ExplodeResponse,
)

__all__ = ["Explode", "ExplodeResponse", "ExplodedBounds", "explode_route"]
