from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class PolygonAttribute(DataClassJsonMixin):
    id: str
    name: str
