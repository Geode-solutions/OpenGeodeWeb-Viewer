from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class ImportProject(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



@dataclass
class ImportProjectResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



import_project_route = Route(
    schema=load_schema(Path(__file__)),
    params=ImportProject,
    response=ImportProjectResponse,
)

__all__ = ["ImportProject", "ImportProjectResponse", "import_project_route"]
