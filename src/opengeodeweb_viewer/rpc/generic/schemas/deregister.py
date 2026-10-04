from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class Deregister(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: str


@dataclass
class DeregisterResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


deregister_route = Route(
    schema=load_schema(__file__),
    params=Deregister,
    response=DeregisterResponse,
)

__all__ = ["Deregister", "DeregisterResponse", "deregister_route"]
