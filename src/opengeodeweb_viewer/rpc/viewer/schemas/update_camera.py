from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import List


@dataclass
class CameraOptions(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    clipping_range: List[float]
    focal_point: List[float]
    position: List[float]
    view_angle: float
    view_up: List[float]


@dataclass
class UpdateCamera(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    camera_options: CameraOptions


@dataclass
class UpdateCameraResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


update_camera_route = Route(
    schema=load_schema(__file__),
    params=UpdateCamera,
    response=UpdateCameraResponse,
)

__all__ = ["CameraOptions", "UpdateCamera", "UpdateCameraResponse", "update_camera_route"]
