from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from typing import List
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass


@dataclass
class RenderingWarnings(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


@dataclass
class RenderingWarningsResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    warnings: List[str]


rendering_warnings_route = Route(
    schema=load_schema(Path(__file__)),
    params=RenderingWarnings,
    response=RenderingWarningsResponse,
)

__all__ = ["RenderingWarnings", "RenderingWarningsResponse", "rendering_warnings_route"]
