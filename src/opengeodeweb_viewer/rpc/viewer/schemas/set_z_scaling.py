from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class SetZScaling(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    z_scale: float


@dataclass
class SetZScalingResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



set_z_scaling_route = Route(
    schema=load_schema(Path(__file__)),
    params=SetZScaling,
    response=SetZScalingResponse,
)

__all__ = ["SetZScaling", "SetZScalingResponse", "set_z_scaling_route"]
