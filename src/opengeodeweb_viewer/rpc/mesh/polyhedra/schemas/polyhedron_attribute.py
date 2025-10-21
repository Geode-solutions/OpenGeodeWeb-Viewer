from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class PolyhedronAttribute(DataClassJsonMixin):
    id: str
    name: str
