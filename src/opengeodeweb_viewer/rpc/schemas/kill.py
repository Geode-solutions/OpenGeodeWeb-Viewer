from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class Kill(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



@dataclass
class KillResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



kill_route = Route(
    schema=load_schema(Path(__file__)),
    params=Kill,
    response=KillResponse,
)

__all__ = ["Kill", "KillResponse", "kill_route"]
