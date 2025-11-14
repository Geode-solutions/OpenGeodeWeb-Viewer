from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List


@dataclass
class CameraOptions(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    clipping_range: List[float]
    focal_point: List[float]
    position: List[float]
    view_angle: float
    view_up: List[float]


@dataclass
class UpdateCamera(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print(self, flush=True)

    camera_options: CameraOptions
