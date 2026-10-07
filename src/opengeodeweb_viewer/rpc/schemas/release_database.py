from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class ReleaseDatabase(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



@dataclass
class ReleaseDatabaseResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



release_database_route = Route(
    schema=load_schema(Path(__file__)),
    params=ReleaseDatabase,
    response=ReleaseDatabaseResponse,
)

__all__ = ["ReleaseDatabase", "ReleaseDatabaseResponse", "release_database_route"]
