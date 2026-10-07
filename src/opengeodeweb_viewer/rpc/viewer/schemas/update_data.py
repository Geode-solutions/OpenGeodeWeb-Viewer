from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class UpdateData(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: str


@dataclass
class UpdateDataResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



update_data_route = Route(
    schema=load_schema(Path(__file__)),
    params=UpdateData,
    response=UpdateDataResponse,
)

__all__ = ["UpdateData", "UpdateDataResponse", "update_data_route"]
