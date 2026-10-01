from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from dataclasses import dataclass
from typing import List


@dataclass
class Texture(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    texture_file_name: str
    texture_name: str


@dataclass
class ApplyTextures(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    id: str
    textures: List[Texture]
