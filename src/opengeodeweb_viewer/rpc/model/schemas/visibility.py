from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class Visibility(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: str
    visibility: bool


@dataclass
class VisibilityResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


visibility_route = Route(
    schema=load_schema(__file__),
    params=Visibility,
    response=VisibilityResponse,
)

__all__ = ["Visibility", "VisibilityResponse", "visibility_route"]
