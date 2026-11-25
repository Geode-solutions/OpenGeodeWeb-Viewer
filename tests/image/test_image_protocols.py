import math
from pathlib import Path
from typing import TYPE_CHECKING

from vtkmodules.vtkCommonCore import VTK_COLOR_MODE_DIRECT_SCALARS
from vtkmodules.vtkIOImage import vtkPNGReader
from vtkmodules.vtkIOXML import vtkXMLImageDataReader
from vtkmodules.vtkRenderingCore import vtkDataSetMapper

from opengeodeweb_viewer.rpc.image.image_protocols import VtkImageView
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView
from opengeodeweb_viewer.vtk_pipeline import VtkPipeline
from tests.mesh.test_mesh_protocols import _SharedObjects

if TYPE_CHECKING:
    from collections.abc import Callable

    from vtkmodules.vtkCommonDataModel import vtkImageData

    from tests.conftest import ServerMonitor

image_id = "123456789012345678901234567image"
DATA_PATH = Path(__file__).parent.parent / "data"
# A rendered pixel lies between the colors of the image points around it
COLOR_TOLERANCE = 3
HAT_SIZE = 512

type Color = tuple[int, int, int]


def _image_rpc(name: str) -> str:
    return VtkImageView.image_prefix + VtkImageView.image_schemas_dict[name]["rpc"]


def _register_image(
    server: ServerMonitor,
    dataset_factory: Callable[..., str],
    viewable_file: str,
    geode_object_type: str,
) -> None:
    dataset_factory(
        data_id=image_id,
        viewable_file=viewable_file,
        viewer_object_type="image",
        geode_object_type=geode_object_type,
        viewer_elements_type="polygons" if geode_object_type == "RasterImage2D" else "polyhedra",
    )
    server.call(_image_rpc("register"), [{"id": image_id, "name": viewable_file}])


def register_image_2d(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    _register_image(server, dataset_factory, "hat_lambert2SG.vti", "RasterImage2D")


def register_image_3d(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    _register_image(server, dataset_factory, "raster_image_3d.vti", "RasterImage3D")


def _screenshot(server: ServerMonitor) -> vtkImageData:
    rpc = VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["take_screenshot"]["rpc"]
    server.call(
        rpc,
        [{"filename": "image_colors", "output_extension": "png", "include_background": True}],
    )
    path = server.test_output_dir / "image_colors.png"
    path.write_bytes(server.get_result(rpc)["blob"])
    reader = vtkPNGReader()
    reader.SetFileName(str(path))
    reader.Update()
    screenshot: vtkImageData = reader.GetOutput()
    return screenshot


def _pixel(screenshot: vtkImageData, x: int, y: int) -> Color:
    width = screenshot.GetDimensions()[0]
    red, green, blue = screenshot.GetPointData().GetScalars().GetTuple(y * width + x)[:3]
    return int(red), int(green), int(blue)


def _center(screenshot: vtkImageData) -> tuple[int, int]:
    width, height, _ = screenshot.GetDimensions()
    return width // 2, height // 2


def _hat_bar_pixel(screenshot: vtkImageData) -> tuple[int, int]:
    """Pixel of the point (60, 256) of the hat image, in the middle of its left bar."""
    # The camera reset fits the bounding sphere of the image in the 30 degrees view angle
    radius = math.hypot(HAT_SIZE - 1, HAT_SIZE - 1) / 2
    pixels_per_point = screenshot.GetDimensions()[1] / 2 * math.cos(math.radians(15)) / radius
    center_x, center_y = _center(screenshot)
    middle = (HAT_SIZE - 1) / 2
    return round(center_x + (60 - middle) * pixels_per_point), center_y


def _image_colors_around(viewable_file: str, i_range: range, j_range: range, k: int) -> list[Color]:
    reader = vtkXMLImageDataReader()
    reader.SetFileName(str(DATA_PATH / viewable_file))
    reader.Update()
    image = reader.GetOutput()
    nx, ny, _ = image.GetDimensions()
    colors = image.GetPointData().GetArray("Color")
    result: list[Color] = []
    for j in j_range:
        for i in i_range:
            red, green, blue = colors.GetTuple3((k * ny + j) * nx + i)
            result.append((int(red), int(green), int(blue)))
    return result


def _hat_bar_colors() -> list[Color]:
    # A single color, around the point (60, 256) wider than a rendered pixel
    return _image_colors_around("hat_lambert2SG.vti", range(50, 71), range(240, 273), 0)


def _assert_between(pixel: Color, colors: list[Color]) -> None:
    for channel in range(3):
        values = [color[channel] for color in colors]
        assert min(values) - COLOR_TOLERANCE <= pixel[channel] <= max(values) + COLOR_TOLERANCE, (
            f"rendered {pixel} is not a color of the image around it: {set(colors)}"
        )


def test_register_image_2d(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    register_image_2d(server, dataset_factory)
    assert server.compare_image("image/register.jpeg")


def test_register_image_2d_true_colors(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    register_image_2d(server, dataset_factory)
    screenshot = _screenshot(server)
    _assert_between(_pixel(screenshot, *_hat_bar_pixel(screenshot)), _hat_bar_colors())


def test_register_image_3d(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    register_image_3d(server, dataset_factory)
    assert server.compare_image("image/register_3d.jpeg")


def test_register_image_3d_true_colors(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    register_image_3d(server, dataset_factory)
    screenshot = _screenshot(server)
    pixel = _pixel(screenshot, *_center(screenshot))
    # The camera looks down on the top face, its center lies between the points (1|2, 1, 1)
    _assert_between(pixel, _image_colors_around("raster_image_3d.vti", range(1, 3), range(1, 2), 1))


def test_image_visibility(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    register_image_2d(server, dataset_factory)
    server.call(_image_rpc("visibility"), [{"id": image_id, "visibility": False}])
    assert server.compare_image("image/visibility.jpeg")
    server.call(_image_rpc("visibility"), [{"id": image_id, "visibility": True}])
    assert server.compare_image("image/register.jpeg")


def test_image_opacity(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    register_image_2d(server, dataset_factory)
    server.call(_image_rpc("opacity"), [{"id": image_id, "opacity": 0.3}])
    assert server.compare_image("image/opacity.jpeg")


def test_deregister_image(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    register_image_2d(server, dataset_factory)
    server.call(_image_rpc("deregister"), [{"id": image_id}])
    assert server.compare_image("image/deregister.jpeg")


def test_image_is_not_pickable(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    register_image_2d(server, dataset_factory)
    screenshot = _screenshot(server)
    x, y = _hat_bar_pixel(screenshot)
    # The image is drawn under the picked pixel
    _assert_between(_pixel(screenshot, x, y), _hat_bar_colors())
    rpc = VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["picked_ids"]["rpc"]
    server.call(rpc, [{"x": x, "y": y, "ids": [image_id]}])
    assert server.get_result(rpc)["array_ids"] == []


def _image_pipeline(view: VtkImageView | VtkMeshView, data_id: str) -> VtkPipeline:
    view.coreServer = _SharedObjects()
    reader = vtkXMLImageDataReader()
    reader.SetFileName(str(DATA_PATH / "hat_lambert2SG.vti"))
    reader.Update()
    pipeline = VtkPipeline(reader, vtkDataSetMapper())
    view.setup_pipeline(pipeline, data_id)
    view.configure_actor(pipeline)
    view.get_data_base()[data_id] = pipeline
    return pipeline


def test_image_visibility_keeps_scalar_bar_hidden() -> None:
    view = VtkImageView()
    pipeline = _image_pipeline(view, image_id)
    view.set_visibility(image_id, visibility=False)
    view.set_visibility(image_id, visibility=True)
    assert not pipeline.scalar_bar.GetVisibility()


def test_mesh_visibility_shows_its_scalar_bar() -> None:
    view = VtkMeshView()
    pipeline = _image_pipeline(view, image_id)
    view.set_visibility(image_id, visibility=False)
    view.set_visibility(image_id, visibility=True)
    assert pipeline.scalar_bar.GetVisibility()


def test_image_actor_shows_unlit_unpickable_colors() -> None:
    view = VtkImageView()
    pipeline = _image_pipeline(view, image_id)
    assert pipeline.mapper.GetScalarVisibility()
    assert pipeline.mapper.GetColorMode() == VTK_COLOR_MODE_DIRECT_SCALARS
    assert not pipeline.actor.GetProperty().GetLighting()
    assert not pipeline.actor.GetPickable()
