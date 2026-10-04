from opengeodeweb_microservice.schemas import Route, load_schema
from dataclasses_json import DataClassJsonMixin
from opengeodeweb_microservice.schemas import print_dataclass
from enum import Enum
from dataclasses import dataclass


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
    schema=load_schema(__file__),
    params=TakeScreenshot,
    response=TakeScreenshotResponse,
)

__all__ = ["TakeScreenshot", "TakeScreenshotResponse", "take_screenshot_route"]
