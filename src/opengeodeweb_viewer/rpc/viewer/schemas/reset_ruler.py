from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class ResetRuler(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


@dataclass
class ResetRulerResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


reset_ruler_route = Route(
    schema=load_schema(__file__),
    params=ResetRuler,
    response=ResetRulerResponse,
)

__all__ = ["ResetRuler", "ResetRulerResponse", "reset_ruler_route"]
