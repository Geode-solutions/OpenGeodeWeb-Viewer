from pathlib import Path
from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import List


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
    textures: List[Texture]


@dataclass
class ApplyTexturesResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    pass


apply_textures_route = Route(
    schema=load_schema(Path(__file__)),
    params=ApplyTextures,
    response=ApplyTexturesResponse,
)

__all__ = ["Texture", "ApplyTextures", "ApplyTexturesResponse", "apply_textures_route"]
