from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkRenderingCore import vtkTexture

from opengeodeweb_viewer.basemap_compose import (
    LayerState,
    basemap_texture,
    compose,
    flat_texture,
    mosaic,
    read_tiles,
    rgba,
    textures,
)

if TYPE_CHECKING:
    from pathlib import Path

SHAPE = (2, 2)


def _image(color: tuple[int, int, int, int]) -> np.ndarray:
    return np.full((*SHAPE, 4), color, np.uint8)


SATELLITE = _image((0, 100, 0, 255))
ROADS = np.zeros((*SHAPE, 4), np.uint8)
ROADS[0, 0] = (255, 0, 0, 255)


def test_rgba_from_any_component_count() -> None:
    grey = np.full((1, 1, 1), 7, np.uint8)
    grey_alpha = np.array([[[7, 128]]], np.uint8)
    rgb = np.array([[[1, 2, 3]]], np.uint8)
    assert rgba(grey).tolist() == [[[7, 7, 7, 255]]]
    assert rgba(grey_alpha).tolist() == [[[7, 7, 7, 128]]]
    assert rgba(rgb).tolist() == [[[1, 2, 3, 255]]]


def test_mosaic_leaves_missing_tiles_transparent() -> None:
    tile = np.full((2, 2, 4), 255, np.uint8)
    image = mosaic({(1, 0): tile}, columns=2, rows=1, size=2)
    assert image.shape == (2, 4, 4)
    assert image[0, 0, 3] == 0
    assert image[0, 2].tolist() == [255, 255, 255, 255]


def test_roads_over_satellite() -> None:
    result = compose([([SATELLITE], 1.0), ([ROADS], 1.0)], SHAPE)
    assert result[0, 0].tolist() == [255, 0, 0, 255]
    # The roads are transparent elsewhere: the satellite shows through
    assert result[1, 1].tolist() == [0, 100, 0, 255]


def test_half_opaque_roads() -> None:
    result = compose([([SATELLITE], 1.0), ([ROADS], 0.5)], SHAPE)
    assert result[0, 0].tolist() == [128, 50, 0, 255]


def test_invisible_layer_changes_nothing() -> None:
    result = compose([([SATELLITE], 1.0), ([ROADS], 0.0)], SHAPE)
    assert np.array_equal(result, SATELLITE)


def test_ign_covers_the_world_source_where_it_has_tiles() -> None:
    world = _image((0, 0, 200, 255))
    ign = np.zeros((*SHAPE, 4), np.uint8)
    ign[0] = (50, 50, 50, 255)
    result = compose([([world, ign], 1.0)], SHAPE)
    assert result[0, 1].tolist() == [50, 50, 50, 255]
    assert result[1, 0].tolist() == [0, 0, 200, 255]


def test_nothing_visible_is_transparent() -> None:
    assert compose([], SHAPE)[0, 0, 3] == 0


def test_map_around_is_the_drape_when_nothing_is_cropped() -> None:
    maps = [("satellite", ["s"]), ("routes", ["r"])]
    images = {"s": SATELLITE, "r": ROADS}
    full, around = textures(
        maps, images, {"satellite": LayerState(), "routes": LayerState()}, SHAPE
    )
    # Nothing cropped: one composition for both textures
    assert around is full


def test_no_map_around_when_no_map_is_visible() -> None:
    maps = [("satellite", ["s"]), ("routes", ["r"])]
    images = {"s": SATELLITE, "r": ROADS}
    states = {"satellite": LayerState(visible=False), "routes": LayerState(visible=False)}
    _, around = textures(maps, images, states, SHAPE)
    assert around is None


def test_cropped_maps_stay_out_of_the_map_around() -> None:
    maps = [("satellite", ["s"]), ("routes", ["r"])]
    images = {"s": SATELLITE, "r": ROADS}
    states = {"satellite": LayerState(), "routes": LayerState(crop=True)}
    full, around = textures(maps, images, states, SHAPE)
    assert full[0, 0].tolist() == [255, 0, 0, 255]
    assert around is not None
    assert around[0, 0].tolist() == [0, 100, 0, 255]
    states = {"satellite": LayerState(crop=True), "routes": LayerState(visible=False)}
    _, around = textures(maps, images, states, SHAPE)
    assert around is None


def test_flat_texture() -> None:
    full, around = vtkTexture(), vtkTexture()
    assert flat_texture(full, around, draped=True) is around
    # Without draped surface the flat map shows every visible map, cropped or not
    assert flat_texture(full, None, draped=False) is full
    assert flat_texture(full, around, draped=False) is full


def test_read_tiles_and_texture(tmp_path: Path) -> None:
    assert read_tiles(tmp_path / "missing") == {}
    texture = basemap_texture(ROADS)
    writer = vtkPNGWriter()
    writer.SetInputData(texture.GetInput())
    writer.SetFileName(str(tmp_path / "1_0.png"))
    writer.Write()
    tiles = read_tiles(tmp_path)
    assert list(tiles) == [(1, 0)]
    # Read back with the north row first, as written
    assert tiles[(1, 0)][0, 0].tolist() == [255, 0, 0, 255]
    assert texture.GetInterpolate()
