from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List


@dataclass
class CameraOptions(DataClassJsonMixin):
    clipping_range: List[float]
    focal_point: List[float]
    position: List[float]
    view_angle: float
    view_up: List[float]


@dataclass
class UpdateCamera(DataClassJsonMixin):
    camera_options: CameraOptions
