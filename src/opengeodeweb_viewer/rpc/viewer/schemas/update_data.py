from dataclasses_json import DataClassJsonMixin
from dataclasses import dataclass


@dataclass
class UpdateData(DataClassJsonMixin):
    id: str
