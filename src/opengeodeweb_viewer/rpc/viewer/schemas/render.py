from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class Render(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



@dataclass
class RenderResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



render_route = Route(
    schema=load_schema(Path(__file__)),
    params=Render,
    response=RenderResponse,
)

__all__ = ["Render", "RenderResponse", "render_route"]
