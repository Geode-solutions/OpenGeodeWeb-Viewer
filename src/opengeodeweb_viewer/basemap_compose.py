"""Maps of the basemap stacked into the textures of its flat map and of its drape."""

from __future__ import annotations

# Standard library imports
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

# Third party imports
import numpy as np
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy
from vtkmodules.vtkCommonCore import VTK_UNSIGNED_CHAR
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkIOImage import vtkImageReader2Factory
from vtkmodules.vtkRenderingCore import vtkTexture

if TYPE_CHECKING:
    from pathlib import Path

RGB = 3
RGBA = 4
MAX_CHANNEL = 255.0


@dataclass(frozen=True)
class LayerState:
    visible: bool = True
    opacity: float = 1.0
    crop: bool = False


def rgba(pixels: np.ndarray) -> np.ndarray:
    """Grey, grey and alpha, RGB or RGBA pixels as RGBA; a missing alpha is opaque."""
    channels = pixels.shape[2]
    colors = pixels[..., :3] if channels >= RGB else np.repeat(pixels[..., :1], 3, axis=2)
    has_alpha = channels in (2, RGBA)
    alpha = pixels[..., -1:] if has_alpha else np.full((*pixels.shape[:2], 1), 255, np.uint8)
    return np.concatenate([colors, alpha], axis=2).astype(np.uint8)


def mosaic(
    tiles: dict[tuple[int, int], np.ndarray], columns: int, rows: int, size: int
) -> np.ndarray:
    """Tiles side by side, row 0 at the north edge; a missing tile is transparent."""
    image = np.zeros((rows * size, columns * size, RGBA), np.uint8)
    for (column, row), tile in tiles.items():
        image[row * size : (row + 1) * size, column * size : (column + 1) * size] = tile
    return image


def _premultiplied(image: np.ndarray) -> np.ndarray:
    pixels = image.astype(np.float32) / MAX_CHANNEL
    pixels[..., :3] *= pixels[..., 3:]
    return pixels


def _over(bottom: np.ndarray, top: np.ndarray) -> np.ndarray:
    return top + bottom * (1.0 - top[..., 3:])


def compose(layers: list[tuple[list[np.ndarray], float]], shape: tuple[int, int]) -> np.ndarray:
    """Each layer, its sources from the bottom up, laid over the layers below with its opacity."""
    result = np.zeros((*shape, RGBA), np.float32)
    for sources, opacity in layers:
        layer = np.zeros_like(result)
        for source in sources:
            layer = _over(layer, _premultiplied(source))
        result = _over(result, layer * opacity)
    alpha = result[..., 3:]
    colors = np.divide(result[..., :3], alpha, out=np.zeros_like(result[..., :3]), where=alpha > 0)
    straight = np.concatenate([colors, alpha], axis=2)
    return np.rint(straight * MAX_CHANNEL).astype(np.uint8)


def textures(
    maps: list[tuple[str, list[str]]],
    images: dict[str, np.ndarray],
    states: dict[str, LayerState],
    shape: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray | None]:
    """Every visible map for the drape; the visible maps not cropped for the map around."""
    visible = [(name, sources) for name, sources in maps if states.get(name, LayerState()).visible]

    def layers(names: list[tuple[str, list[str]]]) -> list[tuple[list[np.ndarray], float]]:
        return [
            (
                [images[source] for source in sources if source in images],
                states.get(name, LayerState()).opacity,
            )
            for name, sources in names
        ]

    around = [
        (name, sources) for name, sources in visible if not states.get(name, LayerState()).crop
    ]
    full = compose(layers(visible), shape)
    if visible and len(around) == len(visible):
        return full, full
    return full, compose(layers(around), shape) if around else None


def flat_texture(full: vtkTexture, around: vtkTexture | None, *, draped: bool) -> vtkTexture:
    # Without draped surface, cropping would hide the whole map: the flat map shows every map
    return around if draped and around is not None else full


def read_tiles(folder: Path) -> dict[tuple[int, int], np.ndarray]:
    """Tiles named <column>_<row>, as RGBA arrays with the north row first."""
    if not folder.is_dir():
        return {}
    tiles: dict[tuple[int, int], np.ndarray] = {}
    for path in folder.iterdir():
        column, row = (int(part) for part in path.stem.split("_"))
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
