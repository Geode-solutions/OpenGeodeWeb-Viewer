from opengeodeweb_microservice.schema_types import DataId
from opengeodeweb_viewer.schema_types import Visibility as VisibilityType
from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class Visibility(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: DataId
    visibility: VisibilityType


@dataclass
class VisibilityResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: DataId
    visibility: VisibilityType


visibility_route = Route(
    schema=load_schema(Path(__file__)),
    params=Visibility,
    response=VisibilityResponse,
)

__all__ = ["Visibility", "VisibilityResponse", "visibility_route"]
