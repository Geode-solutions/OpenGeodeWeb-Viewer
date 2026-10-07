from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


@dataclass
class Texture(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: str
    texture_name: str


@dataclass
class ApplyTextures(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: str
    textures: list[Texture]


@dataclass
class ApplyTexturesResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)



apply_textures_route = Route(
    schema=load_schema(Path(__file__)),
    params=ApplyTextures,
    response=ApplyTexturesResponse,
)

__all__ = ["ApplyTextures", "ApplyTexturesResponse", "Texture", "apply_textures_route"]
