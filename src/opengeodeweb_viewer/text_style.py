# Standard library imports
from dataclasses import dataclass
from typing import TYPE_CHECKING

# Third party imports
if TYPE_CHECKING:
    from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor
    from vtkmodules.vtkRenderingCore import vtkTextProperty

RGB_MAX = 255
GRID_SCALE_AXES = range(3)


@dataclass(frozen=True)
class TextStyle:
    color: tuple[int, int, int] = (0, 0, 0)
    font_family: str = "arial"
    opacity: float = 1.0

    @property
    def is_default(self) -> bool:
        return self == TextStyle()

    @property
    def rgb(self) -> tuple[float, float, float]:
        red, green, blue = self.color
        return (red / RGB_MAX, green / RGB_MAX, blue / RGB_MAX)


def apply_text_property(text_property: vtkTextProperty, style: TextStyle) -> None:
    text_property.SetColor(*style.rgb)
    text_property.SetOpacity(style.opacity)
    if style.font_family == "courier":
        text_property.SetFontFamilyToCourier()
    elif style.font_family == "times":
        text_property.SetFontFamilyToTimes()
    else:
        text_property.SetFontFamilyToArial()


def style_grid_scale(grid_scale: vtkCubeAxesActor, style: TextStyle) -> None:
    for axis in GRID_SCALE_AXES:
        apply_text_property(grid_scale.GetTitleTextProperty(axis), style)
        apply_text_property(grid_scale.GetLabelTextProperty(axis), style)
    for line_property in (
        grid_scale.GetXAxesLinesProperty(),
        grid_scale.GetYAxesLinesProperty(),
        grid_scale.GetZAxesLinesProperty(),
        grid_scale.GetXAxesGridlinesProperty(),
        grid_scale.GetYAxesGridlinesProperty(),
        grid_scale.GetZAxesGridlinesProperty(),
    ):
        line_property.SetColor(*style.rgb)
        line_property.SetOpacity(style.opacity)
