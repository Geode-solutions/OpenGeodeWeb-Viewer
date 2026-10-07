from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class ResetCamera(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



@dataclass
class ResetCameraResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



reset_camera_route = Route(
    schema=load_schema(Path(__file__)),
    params=ResetCamera,
    response=ResetCameraResponse,
)

__all__ = ["ResetCamera", "ResetCameraResponse", "reset_camera_route"]
