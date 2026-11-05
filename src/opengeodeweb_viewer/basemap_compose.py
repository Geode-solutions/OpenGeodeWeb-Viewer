"""Maps of the basemap stacked into the textures of its flat map and of its drape."""

from __future__ import annotations

# Standard library imports
import re
from typing import TYPE_CHECKING, Protocol, cast

# Third party imports
import numpy as np
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy
from vtkmodules.vtkCommonCore import VTK_UNSIGNED_CHAR
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkIOImage import vtkImageReader2Factory
from vtkmodules.vtkRenderingCore import vtkTexture

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path


class LayerState(Protocol):
    """The state of a map, as apply_basemap and basemap_layers send it."""

    @property
    def visible(self) -> bool: ...
    @property
    def opacity(self) -> float: ...
    @property
    def crop(self) -> bool: ...


RGB = 3
RGBA = 4
# The tiles the Back writes: <column>_<row>.png or .jpg
TILE_NAME = re.compile(r"(\d+)_(\d+)\.(png|jpg)")
MAX_CHANNEL = 255.0


def rgba(pixels: np.ndarray) -> np.ndarray:
    """Grey, grey and alpha, RGB or RGBA pixels as RGBA; a missing alpha is opaque."""
    channels = pixels.shape[2]
    colors = (
        pixels[..., :3] if channels >= RGB else np.repeat(pixels[..., :1], 3, axis=2)
    )
    has_alpha = channels in (2, RGBA)
    alpha = (
        pixels[..., -1:]
        if has_alpha
        else np.full((*pixels.shape[:2], 1), 255, np.uint8)
    )
    return np.concatenate([colors, alpha], axis=2).astype(np.uint8)


def mosaic(
    tiles: dict[tuple[int, int], np.ndarray],
    columns: int,
    rows: int,
    tile_shape: tuple[int, ...],
) -> np.ndarray:
    """Tiles side by side, row 0 at the north edge; a missing tile is transparent."""
    height, width = tile_shape
    image = np.zeros((rows * height, columns * width, RGBA), np.uint8)
    for (column, row), tile in tiles.items():
        image[
            row * height : (row + 1) * height, column * width : (column + 1) * width
        ] = tile
    return image


def _premultiplied(image: np.ndarray) -> np.ndarray:
    pixels = image.astype(np.float32) / MAX_CHANNEL
    pixels[..., :3] *= pixels[..., 3:]
    return pixels


def _over(bottom: np.ndarray, top: np.ndarray) -> None:
    """Lays top over bottom, in place: no image sized temporary."""
    bottom *= 1.0 - top[..., 3:]
    bottom += top


def compose(
    layers: list[tuple[list[np.ndarray], float]], shape: tuple[int, ...]
) -> np.ndarray:
    """Each layer, its sources from the bottom up, laid over the layers below with its opacity."""
    result = np.zeros((*shape, RGBA), np.float32)
    for sources, opacity in layers:
        # A transparent layer changes nothing
        if not sources or opacity <= 0:
            continue
        layer = _premultiplied(sources[0])
        for source in sources[1:]:
            _over(layer, _premultiplied(source))
        layer *= opacity
        _over(result, layer)
    alpha = result[..., 3:]
    # Premultiplied colours are 0 where the alpha is: they stay 0
    np.divide(result[..., :3], alpha, out=result[..., :3], where=alpha > 0)
    result *= MAX_CHANNEL
    return np.rint(result, out=result).astype(np.uint8)


def textures(
    maps: list[tuple[str, list[str]]],
    images: dict[str, np.ndarray],
    states: Mapping[str, LayerState],
    shape: tuple[int, ...],
) -> tuple[np.ndarray, np.ndarray | None]:
    """Every visible map for the drape; the visible maps not cropped for the map around."""
    # A map the front did not describe is not shown
    visible = [
        (states[name], sources)
        for name, sources in maps
        if name in states and states[name].visible
    ]
    around = [(state, sources) for state, sources in visible if not state.crop]

    def layers(
        shown: list[tuple[LayerState, list[str]]],
    ) -> list[tuple[list[np.ndarray], float]]:
        return [
            ([images[source] for source in sources], state.opacity)
            for state, sources in shown
        ]

    full = compose(layers(visible), shape)
    if not around:
        return full, None
    if len(around) == len(visible):
        return full, full
    return full, compose(layers(around), shape)


def read_tiles(folder: Path) -> dict[tuple[int, int], np.ndarray]:
    """Tiles named <column>_<row>, as RGBA arrays with the north row first; other files skipped."""
    if not folder.is_dir():
        return {}
    tiles: dict[tuple[int, int], np.ndarray] = {}
    for path in folder.iterdir():
        name = TILE_NAME.fullmatch(path.name)
        if name is None:
            continue
        column, row = int(name[1]), int(name[2])
        reader = vtkImageReader2Factory.CreateImageReader2(str(path))
        reader.SetFileName(str(path))
        reader.Update()
        image = cast("vtkImageData", reader.GetOutput())
        width, height, _ = image.GetDimensions()
        scalars = vtk_to_numpy(image.GetPointData().GetScalars())  # type: ignore[no-untyped-call]
        pixels = scalars.reshape(height, width, -1)
        # VTK images start at the south edge
        tiles[(column, row)] = rgba(pixels[::-1])
    return tiles


def basemap_texture(image: np.ndarray) -> vtkTexture:
    height, width, _ = image.shape
    data = vtkImageData()
    data.SetDimensions(width, height, 1)
    flat = np.ascontiguousarray(image[::-1]).reshape(-1, RGBA)
    data.GetPointData().SetScalars(
        numpy_to_vtk(flat, deep=True, array_type=VTK_UNSIGNED_CHAR)  # type: ignore[no-untyped-call]
    )
    texture = vtkTexture()
    texture.SetInputData(data)
    texture.InterpolateOn()
    return texture
