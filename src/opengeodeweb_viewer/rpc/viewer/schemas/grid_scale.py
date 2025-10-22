from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class GridScale(DataClassJsonMixin):
    visibility: bool
