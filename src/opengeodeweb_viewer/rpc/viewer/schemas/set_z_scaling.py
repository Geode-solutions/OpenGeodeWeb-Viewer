from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class SetZScaling(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    z_scale: float


@dataclass
class SetZScalingResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


set_z_scaling_route = Route(
    schema=load_schema(__file__),
    params=SetZScaling,
    response=SetZScalingResponse,
)

__all__ = ["SetZScaling", "SetZScalingResponse", "set_z_scaling_route"]
