# Standard library imports
from typing import TYPE_CHECKING

# Third party imports
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray, vtkPolyData
from vtkmodules.vtkFiltersSources import vtkLineSource, vtkRegularPolygonSource
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor, vtkCaptionActor2D
from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper, vtkPropAssembly

# Local application imports
from opengeodeweb_viewer.text_style import TextStyle, apply_text_property

if TYPE_CHECKING:
    from vtkmodules.vtkCommonExecutionModel import vtkAlgorithm
    from vtkmodules.vtkRenderingCore import vtkProp, vtkTextProperty

# VTK's own caption look, kept while the scene text style is the default one
DEFAULT_CAPTION_COLOR = (1.0, 1.0, 1.0)

COMPASS_RING_NAME = "compass_ring"
COMPASS_RING_SIDES = 64
COMPASS_RING_WIDTH = 2.0
COMPASS_NEEDLE_LENGTH = 0.85
COMPASS_NEEDLE_HALF_WIDTH = 0.2
COMPASS_NORTH_COLOR = (0.85, 0.2, 0.18)
COMPASS_SOUTH_COLOR = (0.92, 0.92, 0.92)
COMPASS_LABEL_OFFSET = 1.6
COMPASS_LABEL_FONT_SIZE = 14
# Captions sit on their baseline: lower them so they look vertically centered
COMPASS_LABEL_DROP = 0.35
COMPASS_LABELS = (
    ("N", (0.0, COMPASS_LABEL_OFFSET - COMPASS_LABEL_DROP, 0.0)),
    ("S", (0.0, -COMPASS_LABEL_OFFSET - COMPASS_LABEL_DROP, 0.0)),
    ("E", (COMPASS_LABEL_OFFSET, -COMPASS_LABEL_DROP, 0.0)),
    ("W", (-COMPASS_LABEL_OFFSET, -COMPASS_LABEL_DROP, 0.0)),
)
COMPASS_EXTENT = 2.0


def _flat_actor(source: vtkAlgorithm | vtkPolyData, color: tuple[float, float, float]) -> vtkActor:
    mapper = vtkPolyDataMapper()
    if isinstance(source, vtkPolyData):
        mapper.SetInputData(source)
    else:
        mapper.SetInputConnection(source.GetOutputPort())
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor_property = actor.GetProperty()
    actor_property.SetColor(*color)
    actor_property.SetAmbient(1.0)
    actor_property.SetDiffuse(0.0)
    return actor


def _compass_ring() -> vtkActor:
    source = vtkRegularPolygonSource()
    source.SetNumberOfSides(COMPASS_RING_SIDES)
    source.SetRadius(1.0)
    source.GeneratePolygonOff()
    actor = _flat_actor(source, DEFAULT_CAPTION_COLOR)
    actor.GetProperty().SetLineWidth(COMPASS_RING_WIDTH)
    actor.SetObjectName(COMPASS_RING_NAME)
    return actor


def _compass_needle_half(tip_y: float, color: tuple[float, float, float]) -> vtkActor:
    points = vtkPoints()
    points.InsertNextPoint(0.0, tip_y, 0.0)
    points.InsertNextPoint(COMPASS_NEEDLE_HALF_WIDTH, 0.0, 0.0)
    points.InsertNextPoint(-COMPASS_NEEDLE_HALF_WIDTH, 0.0, 0.0)
    triangle = vtkCellArray()
    triangle.InsertNextCell(3, [0, 1, 2])
    polydata = vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetPolys(triangle)
    return _flat_actor(polydata, color)


def _compass_label(label: str, position: tuple[float, float, float]) -> vtkCaptionActor2D:
    caption = vtkCaptionActor2D()
    caption.SetCaption(label)
    caption.SetAttachmentPoint(*position)
    caption.BorderOff()
    caption.LeaderOff()
    # Unscaled text is justified around the caption position: center it on the attachment point
    caption.SetPosition(0, 0)
    caption.GetTextActor().SetTextScaleModeToNone()
    text_property = caption.GetCaptionTextProperty()
    text_property.SetFontSize(COMPASS_LABEL_FONT_SIZE)
    text_property.SetJustificationToCentered()
    text_property.SetVerticalJustificationToCentered()
    text_property.ItalicOff()
    return caption


def _compass_extent() -> vtkActor:
    # 2D captions do not count in the marker bounds: an invisible diagonal keeps them in frame
    source = vtkLineSource()
    source.SetPoint1(-COMPASS_EXTENT, -COMPASS_EXTENT, 0.0)
    source.SetPoint2(COMPASS_EXTENT, COMPASS_EXTENT, 0.0)
    actor = _flat_actor(source, DEFAULT_CAPTION_COLOR)
    actor.GetProperty().SetOpacity(0.0)
    return actor


def build_compass() -> vtkPropAssembly:
    compass = vtkPropAssembly()
    compass.AddPart(_compass_ring())
    compass.AddPart(_compass_needle_half(COMPASS_NEEDLE_LENGTH, COMPASS_NORTH_COLOR))
    compass.AddPart(_compass_needle_half(-COMPASS_NEEDLE_LENGTH, COMPASS_SOUTH_COLOR))
    for label, position in COMPASS_LABELS:
        compass.AddPart(_compass_label(label, position))
    compass.AddPart(_compass_extent())
    return compass


def build_marker(marker: str) -> vtkProp:
    if marker == "compass":
        return build_compass()
    return vtkAxesActor()


def _assembly_parts(assembly: vtkPropAssembly) -> list[vtkProp]:
    parts = assembly.GetParts()
    parts.InitTraversal()
    return [parts.GetNextProp() for _ in range(parts.GetNumberOfItems())]


def _style_caption(text_property: vtkTextProperty, style: TextStyle) -> None:
    if style.is_default:
        text_property.SetColor(*DEFAULT_CAPTION_COLOR)
        text_property.SetOpacity(1.0)
        text_property.SetFontFamilyToArial()
        text_property.ShadowOn()
        return
    apply_text_property(text_property, style)
    # VTK draws the shadow in the inverse color, which halos custom colors
    text_property.ShadowOff()


def style_marker(marker: vtkProp, style: TextStyle) -> None:
    if isinstance(marker, vtkAxesActor):
        for caption in (
            marker.GetXAxisCaptionActor2D(),
            marker.GetYAxisCaptionActor2D(),
            marker.GetZAxisCaptionActor2D(),
        ):
            _style_caption(caption.GetCaptionTextProperty(), style)
        return
    if isinstance(marker, vtkPropAssembly):
        ring_color = DEFAULT_CAPTION_COLOR if style.is_default else style.rgb
        ring_opacity = 1.0 if style.is_default else style.opacity
        for part in _assembly_parts(marker):
            if isinstance(part, vtkCaptionActor2D):
                _style_caption(part.GetCaptionTextProperty(), style)
            elif isinstance(part, vtkActor) and part.GetObjectName() == COMPASS_RING_NAME:
                part.GetProperty().SetColor(*ring_color)
                part.GetProperty().SetOpacity(ring_opacity)
