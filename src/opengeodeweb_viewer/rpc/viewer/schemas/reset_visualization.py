from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class ResetVisualization(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



@dataclass
class ResetVisualizationResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



reset_visualization_route = Route(
    schema=load_schema(Path(__file__)),
    params=ResetVisualization,
    response=ResetVisualizationResponse,
)

__all__ = ["ResetVisualization", "ResetVisualizationResponse", "reset_visualization_route"]
