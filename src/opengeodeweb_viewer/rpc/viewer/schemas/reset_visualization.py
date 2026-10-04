from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class ResetVisualization(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


@dataclass
class ResetVisualizationResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


reset_visualization_route = Route(
    schema=load_schema(__file__),
    params=ResetVisualization,
    response=ResetVisualizationResponse,
)

__all__ = ["ResetVisualization", "ResetVisualizationResponse", "reset_visualization_route"]
