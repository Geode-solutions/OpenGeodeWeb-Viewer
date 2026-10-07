from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class CameraOptions(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    clipping_range: list[float]
    focal_point: list[float]
    position: list[float]
    view_angle: float
    view_up: list[float]


@dataclass
class UpdateCamera(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    camera_options: CameraOptions


@dataclass
class UpdateCameraResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



update_camera_route = Route(
    schema=load_schema(Path(__file__)),
    params=UpdateCamera,
    response=UpdateCameraResponse,
)

__all__ = ["CameraOptions", "UpdateCamera", "UpdateCameraResponse", "update_camera_route"]
