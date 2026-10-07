from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class ResetRuler(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



@dataclass
class ResetRulerResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



reset_ruler_route = Route(
    schema=load_schema(Path(__file__)),
    params=ResetRuler,
    response=ResetRulerResponse,
)

__all__ = ["ResetRuler", "ResetRulerResponse", "reset_ruler_route"]
