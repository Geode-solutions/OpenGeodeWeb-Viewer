from opengeodeweb_microservice.schema_types import DataId
from opengeodeweb_viewer.schema_types import EdgeWidth
from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class Width(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: DataId
    width: EdgeWidth


@dataclass
class WidthResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


width_route = Route(
    schema=load_schema(Path(__file__)),
    params=Width,
    response=WidthResponse,
)

__all__ = ["Width", "WidthResponse", "width_route"]
