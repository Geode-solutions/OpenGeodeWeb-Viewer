from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class Explode(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    explode_factor: float
    ids: list[str]


@dataclass
class ExplodeResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



explode_route = Route(
    schema=load_schema(Path(__file__)),
    params=Explode,
    response=ExplodeResponse,
)

__all__ = ["Explode", "ExplodeResponse", "explode_route"]
