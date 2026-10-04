from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class ResetCamera(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


@dataclass
class ResetCameraResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


reset_camera_route = Route(
    schema=load_schema(__file__),
    params=ResetCamera,
    response=ResetCameraResponse,
)

__all__ = ["ResetCamera", "ResetCameraResponse", "reset_camera_route"]
