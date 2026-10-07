from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import Route, load_schema, print_dataclass


class OutputExtension(Enum):
    JPG = "jpg"
    PNG = "png"


@dataclass
class TakeScreenshot(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    filename: str
    include_background: bool
    output_extension: OutputExtension


@dataclass
class TakeScreenshotResponse(DataClassJsonMixin):
    def __post_init__(self) -> None:
        print_dataclass(self)

    blob: str


take_screenshot_route = Route(
    schema=load_schema(Path(__file__)),
    params=TakeScreenshot,
    response=TakeScreenshotResponse,
)

__all__ = ["TakeScreenshot", "TakeScreenshotResponse", "take_screenshot_route"]
