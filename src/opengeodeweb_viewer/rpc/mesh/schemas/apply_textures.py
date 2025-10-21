from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass
from typing import List


@dataclass
class Texture(DataClassJsonMixin):
    id: str
    texture_name: str


@dataclass
class ApplyTextures(DataClassJsonMixin):
    id: str
    textures: List[Texture]
