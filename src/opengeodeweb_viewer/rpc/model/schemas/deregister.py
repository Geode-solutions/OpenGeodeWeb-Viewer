from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class Deregister(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: str


@dataclass
class DeregisterResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



deregister_route = Route(
    schema=load_schema(Path(__file__)),
    params=Deregister,
    response=DeregisterResponse,
)

__all__ = ["Deregister", "DeregisterResponse", "deregister_route"]
