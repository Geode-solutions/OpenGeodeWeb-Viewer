import logging
from typing import TYPE_CHECKING

# Standard library imports
import pytest

from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from opengeodeweb_viewer.rpc.mesh.points.attribute.vertex.points_attribute_vertex_protocols import (
    VtkMeshPointsAttributeVertexView,
)

# Third party imports
# Local application imports
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView

# Local application imports
from tests.mesh.points.attribute.vertex.test_points_attribute_vertex_protocols import (
    mesh_id as points_mesh_id,
)
from tests.mesh.points.attribute.vertex.test_points_attribute_vertex_protocols import (
    test_register as test_register_points,
)
from tests.mesh.test_mesh_protocols import test_register_mesh

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests.conftest import ServerMonitor

# Local constants
logger = logging.getLogger(__name__)


mesh_id = "12345678901234567890123456789012"


def test_reset_visualization(server: ServerMonitor) -> None:
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["reset_visualization"]["rpc"]
    )
    assert server.compare_image("viewer/reset_visualization.jpeg")


def test_reset_camera(server: ServerMonitor) -> None:
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["reset_camera"]["rpc"]
    )
    assert server.compare_image("viewer/reset_camera.jpeg")


def test_set_viewer_background_color(server: ServerMonitor) -> None:
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["set_background_color"]["rpc"],
        [{"color": {"r": 0, "g": 0, "b": 255}}],
    )
    assert server.compare_image("viewer/set_background_color.jpeg")


def test_set_text_style(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_grid_scale(server, dataset_factory)
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["set_text_style"]["rpc"],
        [{"color": {"r": 255, "g": 0, "b": 0}, "font_family": "courier", "opacity": 0.5}],
    )
    assert server.compare_image("viewer/set_text_style.jpeg")


def test_set_text_style_then_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_reset_visualization(server)
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["set_text_style"]["rpc"],
        [{"color": {"r": 255, "g": 0, "b": 0}, "font_family": "times", "opacity": 1.0}],
    )
    test_register_points(server, dataset_factory)
    server.call(
        VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_prefix
        + VtkMeshPointsAttributeVertexView.mesh_points_attribute_vertex_schemas_dict["attribute"][
            "rpc"
        ],
        [
            {
                "id": points_mesh_id,
                "name": "lambert2SG",
                "item": 0,
                "points": [0.0, 0, 0, 1.0, 1.0, 1.0, 0, 0],
                "minimum": 0.0,
                "maximum": 1.0,
                "no_data_color": {"red": 128, "green": 128, "blue": 128, "alpha": 1.0},
            }
        ],
    )
    assert server.compare_image("viewer/set_text_style_then_attribute.jpeg")


def test_get_point_position(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["get_point_position"]["rpc"],
        [{"x": 0, "y": 0}],
    )
    result = server.get_result(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["get_point_position"]["rpc"]
    )
    if result is None:
        return
    if not isinstance(result, dict):
        pytest.fail(f"Result is not a dict: {result!r}")
    assert "x" in result, f"No 'x' in result: {result}"
    assert "y" in result, f"No 'y' in result: {result}"
    assert "z" in result, f"No 'z' in result: {result}"
    x = result["x"]
    y = result["y"]
    z = result["z"]
    assert type(x) is float
    assert type(y) is float
    assert type(z) is float


def test_take_screenshot(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)

    # Take a screenshot with background jpg
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["take_screenshot"]["rpc"],
        [
            {
                "filename": "take_screenshot_with_background",
                "output_extension": "jpg",
                "include_background": True,
            }
        ],
    )

    blob = server.get_result(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["take_screenshot"]["rpc"]
    )["blob"]
    assert type(blob) is bytes

    first_image_path = server.test_output_dir / "test.jpg"
    first_image_path.write_bytes(blob)
    second_image_path = server.images_dir_path / "viewer/take_screenshot_with_background.jpg"

    assert server.images_diff(first_image_path, second_image_path) == 0.0

    # Take a screenshot without background png
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["take_screenshot"]["rpc"],
        [
            {
                "filename": "take_screenshot_without_background",
                "output_extension": "png",
                "include_background": False,
            }
        ],
    )

    blob = server.get_result(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["take_screenshot"]["rpc"]
    )["blob"]
    assert type(blob) is bytes

    first_image_path = server.test_output_dir / "test.png"
    first_image_path.write_bytes(blob)
    second_image_path = server.images_dir_path / "viewer/take_screenshot_without_background.png"

    assert server.images_diff(first_image_path, second_image_path) == 0.0

    # Take a screenshot with background png
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["take_screenshot"]["rpc"],
        [
            {
                "filename": "take_screenshot_with_background",
                "output_extension": "png",
                "include_background": True,
            }
        ],
    )

    blob = server.get_result(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["take_screenshot"]["rpc"]
    )["blob"]
    assert type(blob) is bytes

    first_image_path = server.test_output_dir / "test.png"
    first_image_path.write_bytes(blob)
    second_image_path = server.images_dir_path / "viewer/take_screenshot_with_background.png"

    assert server.images_diff(first_image_path, second_image_path) == 0.0


def test_picked_ids(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_register_mesh(server, dataset_factory)

    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["picked_ids"]["rpc"],
        [{"x": 0, "y": 0, "ids": ["00000000000000000000000123456789"]}],
    )
    response = server.get_rpc_response(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["picked_ids"]["rpc"]
    )
    logger.info("picked_ids response: %r", response)
    if "result" not in response:
        logger.warning("No 'result' key in picked_ids response: %r", response)
        return
    result = response["result"]
    if result is None:
        logger.warning("picked_ids result is None")
        return
    if not isinstance(result, dict):
        logger.warning("picked_ids result is not a dict: %r", result)
        return
    assert "array_ids" in result
    array_ids = result["array_ids"]
    assert isinstance(array_ids, list)


def test_grid_scale(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    data_id = "00000000000000000000000123456789"
    dataset_factory(data_id=data_id, viewable_file="hat.vtp", viewer_elements_type="polygons")
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["reset_visualization"]["rpc"],
    )
    assert server.compare_image("viewer/reset_visualization.jpeg")
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": data_id, "name": "hat.vtp"}],
    )
    assert server.compare_image("viewer/register_hat.jpeg")

    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["grid_scale"]["rpc"],
        [{"visibility": True}],
    )
    assert server.compare_image("viewer/grid_scale_on.jpeg")


def test_axes(server: ServerMonitor) -> None:

    test_reset_visualization(server)

    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["axes"]["rpc"],
        [{"visibility": False}],
    )

    assert server.compare_image("viewer/axes_off.jpeg")


def test_set_orientation_widget_compass(server: ServerMonitor) -> None:
    test_reset_visualization(server)
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["set_text_style"]["rpc"],
        [{"color": {"r": 255, "g": 0, "b": 0}, "font_family": "arial", "opacity": 1.0}],
    )
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["set_orientation_widget"]["rpc"],
        [{"marker": "compass"}],
    )
    assert server.compare_image("viewer/orientation_widget_compass.jpeg")

    test_reset_visualization(server)


def test_set_text_style_after_compass(server: ServerMonitor) -> None:
    test_reset_visualization(server)
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["set_orientation_widget"]["rpc"],
        [{"marker": "compass"}],
    )
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["set_text_style"]["rpc"],
        [{"color": {"r": 255, "g": 0, "b": 0}, "font_family": "arial", "opacity": 1.0}],
    )
    assert server.compare_image("viewer/orientation_widget_compass.jpeg")

    test_reset_visualization(server)


def test_orientation_widget_keeps_visibility(server: ServerMonitor) -> None:
    test_reset_visualization(server)
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["axes"]["rpc"],
        [{"visibility": False}],
    )
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["set_orientation_widget"]["rpc"],
        [{"marker": "compass"}],
    )
    assert server.compare_image("viewer/axes_off.jpeg")


def test_update_camera(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)

    camera_options = {
        "focal_point": [-0.034399999999999986, 2.4513515, -0.10266900000000012],
        "view_up": [0.48981180389508683, 0.8647097694977263, -0.11118188386706776],
        "position": [-17.277630202755162, 13.419047188880267, 9.232808007244259],
        "view_angle": 30.0,
        "clipping_range": [11.403438348232822, 36.44815678922037],
    }

    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["update_camera"]["rpc"],
        [
            {
                "camera_options": camera_options,
            }
        ],
    )
    assert server.compare_image("viewer/update_camera.jpeg")


def test_render(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)

    camera_options = {
        "focal_point": [-0.034399999999999986, 2.4513515, -0.10266900000000012],
        "view_up": [0.48981180389508683, 0.8647097694977263, -0.11118188386706776],
        "position": [-17.277630202755162, 13.419047188880267, 9.232808007244259],
        "view_angle": 30.0,
        "clipping_range": [11.403438348232822, 36.44815678922037],
    }

    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["update_camera"]["rpc"],
        [
            {
                "camera_options": camera_options,
            }
        ],
    )

    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["render"]["rpc"],
    )

    assert server.compare_image("viewer/render.jpeg")


def test_set_z_scaling(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    dataset_factory(
        data_id="00000000000000000000000123456789",
        viewable_file="polygon_attribute.vtp",
        viewer_elements_type="polygons",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "00000000000000000000000123456789", "name": "hat.vtp"}],
    )
    assert server.compare_image("viewer/polygon_attribute.jpeg")

    dataset_factory(
        data_id="00000000000000000000000987654321",
        viewable_file="vertex_attribute.vtp",
        viewer_elements_type="polygons",
    )
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "00000000000000000000000987654321", "name": "vertex_attribute.vtp"}],
    )
    assert server.compare_image("viewer/vertex_and_polygon_attribute.jpeg")

    camera_options = {
        "focal_point": [6.05, 5.7, 1.5],
        "view_up": [-0.019853719211915175, 0.9994261532466464, 0.02744438084681784],
        "position": [-19.898328271321652, 5.221831172558093, 0.1417477620371277],
        "view_angle": 30.0,
        "clipping_range": [20.16946812228507, 31.94497749971925],
    }

    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["update_camera"]["rpc"],
        [
            {
                "camera_options": camera_options,
            }
        ],
    )

    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["set_z_scaling"]["rpc"],
        [{"z_scale": 2.5}],
    )
    assert server.compare_image("viewer/set_z_scaling.jpeg")


def test_combined_scaling_and_grid(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["reset_visualization"]["rpc"],
    )
    assert server.compare_image("viewer/reset_visualization.jpeg")
    dataset_factory(data_id=mesh_id, viewable_file="hat.vtp", viewer_elements_type="polygons")
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "name": "hat.vtp"}],
    )
    assert server.compare_image("viewer/register_hat.jpeg")
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["grid_scale"]["rpc"],
        [{"visibility": True}],
    )
    assert server.compare_image("viewer/grid_scale_on.jpeg")
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["set_z_scaling"]["rpc"],
        [{"z_scale": 2.5}],
    )
    assert server.compare_image("viewer/combined_scaling_and_grid.jpeg")


def test_clipping_planes(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["clipping_planes"]["rpc"],
        [
            {
                "ids": [mesh_id],
                "planes": [
                    {
                        "origin": [0.0, 0.0, 0.0],
                        "normal": [1.0, 0.0, 0.0],
                    }
                ],
            }
        ],
    )


def test_shrink(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["shrink"]["rpc"],
        [
            {
                "ids": [mesh_id],
                "shrink_factor": 0.8,
            }
        ],
    )
    assert server.compare_image("viewer/shrink.jpeg")


def test_explode_mesh(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["explode"]["rpc"],
        [{"ids": [mesh_id], "explode_factor": 0.5}],
    )
    assert server.compare_image("mesh/register.jpeg")


def test_clipping_then_shrink(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["clipping_planes"]["rpc"],
        [
            {
                "ids": [mesh_id],
                "planes": [
                    {
                        "origin": [0.0, 0.0, 0.0],
                        "normal": [1.0, 0.0, 0.0],
                    }
                ],
            }
        ],
    )
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["shrink"]["rpc"],
        [
            {
                "ids": [mesh_id],
                "shrink_factor": 0.8,
            }
        ],
    )
    assert server.compare_image("viewer/clipping_then_shrink.jpeg")


def test_shrink_then_clipping(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["shrink"]["rpc"],
        [
            {
                "ids": [mesh_id],
                "shrink_factor": 0.8,
            }
        ],
    )
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["clipping_planes"]["rpc"],
        [
            {
                "ids": [mesh_id],
                "planes": [
                    {
                        "origin": [0.0, 0.0, 0.0],
                        "normal": [1.0, 0.0, 0.0],
                    }
                ],
            }
        ],
    )
    assert server.compare_image("viewer/clipping_then_shrink.jpeg")


def test_ruler(server: ServerMonitor) -> None:
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["reset_visualization"]["rpc"]
    )
    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["ruler"]["rpc"],
        [
            {
                "points": [[-0.2, -0.2, 0.0], [0.2, 0.2, 0.0]],
            }
        ],
    )
    assert server.compare_image("viewer/ruler.jpeg")
