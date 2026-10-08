from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class Size(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: str
    size: float


@dataclass
class SizeResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


size_route = Route(
    schema=load_schema(Path(__file__)),
    params=Size,
    response=SizeResponse,
)

__all__ = ["Size", "SizeResponse", "size_route"]
