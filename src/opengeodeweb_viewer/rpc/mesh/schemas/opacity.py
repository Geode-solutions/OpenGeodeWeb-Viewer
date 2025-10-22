from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class Opacity(DataClassJsonMixin):
    id: str
    opacity: float
