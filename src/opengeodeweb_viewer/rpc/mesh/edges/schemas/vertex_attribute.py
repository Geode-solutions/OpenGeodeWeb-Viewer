from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class VertexAttribute(DataClassJsonMixin):
    id: str
    name: str
