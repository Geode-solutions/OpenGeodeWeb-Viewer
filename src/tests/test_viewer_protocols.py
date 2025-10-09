# Standard library imports
import os
from typing import Callable

# Third party imports

# Local application imports
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView

# Local application imports
from tests.mesh.test_mesh_protocols import test_register_mesh
from tests.conftest import ServerMonitor


def test_reset_visualization(server: ServerMonitor) -> None:
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["reset_visualization"]["rpc"]
    )
    assert server.compare_image(3, "viewer/reset_visualization.jpeg") == True


def test_reset_camera(server: ServerMonitor) -> None:
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["reset_camera"]["rpc"]
    )
    assert server.compare_image(3, "viewer/reset_camera.jpeg") == True


def test_set_viewer_background_color(server: ServerMonitor) -> None:
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["set_background_color"]["rpc"],
        [{"color": {"r": 0, "g": 0, "b": 255}}],
    )
    assert server.compare_image(3, "viewer/set_background_color.jpeg") == True


def test_get_point_position(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["get_point_position"]["rpc"],
        [{"x": 0, "y": 0}],
    )
    response = server.get_response()
    if response is None:
        assert False, "Response is None from get_point_position"
    if not isinstance(response, dict) or "result" not in response:
        assert False, f"No 'result' key in response: {response!r}"
    result = response["result"]
    if result is None:
        return
    if not isinstance(result, dict):
        assert False, f"Result is not a dict: {result!r}"
    assert "x" in result, f"No 'x' in result: {result}"
    assert "y" in result, f"No 'y' in result: {result}"
    assert "z" in result, f"No 'z' in result: {result}"
    x = result["x"]
    y = result["y"]
    z = result["z"]
    assert type(x) is float
    assert type(y) is float
    assert type(z) is float


def test_take_screenshot(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    # Take a screenshot with background jpg
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["take_screenshot"]["rpc"],
        [
            {
                "filename": "take_screenshot_with_background",
                "output_extension": "jpg",
                "include_background": True,
            }
        ],
    )

    server.get_response()
    blob = server.get_response()
    assert type(blob) is bytes

    with open(os.path.join(server.test_output_dir, "test.jpg"), "wb") as f:
        f.write(blob)
        f.close()
    first_image_path = os.path.join(server.test_output_dir, "test.jpg")
    second_image_path = os.path.join(
        server.images_dir_path, "viewer/take_screenshot_with_background.jpg"
    )

    assert server.images_diff(first_image_path, second_image_path) == 0.0

    # Take a screenshot without background png
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["take_screenshot"]["rpc"],
        [
            {
                "filename": "take_screenshot_without_background",
                "output_extension": "png",
                "include_background": False,
            }
        ],
    )

    server.get_response()
    server.get_response()
    blob = server.get_response()
    print(f"{blob!r}", flush=True)
    assert type(blob) is bytes

    with open(os.path.join(server.test_output_dir, "test.png"), "wb") as f:
        f.write(blob)
        f.close()
    first_image_path = os.path.join(server.test_output_dir, "test.png")
    second_image_path = os.path.join(
        server.images_dir_path, "viewer/take_screenshot_without_background.png"
    )

    assert server.images_diff(first_image_path, second_image_path) == 0.0

    # Take a screenshot with background png
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["take_screenshot"]["rpc"],
        [
            {
                "filename": "take_screenshot_with_background",
                "output_extension": "png",
                "include_background": True,
            }
        ],
    )

    server.get_response()
    server.get_response()
    blob = server.get_response()
    print(f"{blob!r}", flush=True)
    assert type(blob) is bytes

    with open(os.path.join(server.test_output_dir, "test.png"), "wb") as f:
        f.write(blob)
        f.close()
    first_image_path = os.path.join(server.test_output_dir, "test.png")
    second_image_path = os.path.join(
        server.images_dir_path, "viewer/take_screenshot_with_background.png"
    )

    assert server.images_diff(first_image_path, second_image_path) == 0.0


def test_picked_ids(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_register_mesh(server, dataset_factory)

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["picked_ids"]["rpc"],
        [{"x": 0, "y": 0, "ids": ["123456789"]}],
    )
    response = server.get_response()
    print(f"picked_ids response: {response!r}", flush=True)
    if response is None:
        print("Warning: picked_ids returned None response", flush=True)
        return
    if not isinstance(response, dict) or "result" not in response:
        print(
            f"Warning: No 'result' key in picked_ids response: {response!r}", flush=True
        )
        return
    result = response["result"]
    if result is None:
        print("Warning: picked_ids result is None", flush=True)
        return
    if not isinstance(result, dict):
        print(f"Warning: picked_ids result is not a dict: {result!r}", flush=True)
        return
    assert "array_ids" in result
    array_ids = result["array_ids"]
    assert isinstance(array_ids, list)


def test_grid_scale(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    data_id = "123456789"
    dataset_factory(id=data_id, viewable_file_name="hat.vtp")
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["reset_visualization"]["rpc"],
    )
    assert server.compare_image(3, "viewer/reset_visualization.jpeg") == True
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": data_id}],
    )
    assert server.compare_image(3, "viewer/register_hat.jpeg") == True

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["grid_scale"]["rpc"],
        [{"visibility": True}],
    )
    assert server.compare_image(3, "viewer/grid_scale_on.jpeg") == True


def test_axes(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:

    test_reset_visualization(server)

    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["axes"]["rpc"],
        [{"visibility": False}],
    )

    assert server.compare_image(3, "viewer/axes_off.jpeg") == True


def test_update_camera(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    camera_options = {
        "focal_point": [-0.034399999999999986, 2.4513515, -0.10266900000000012],
        "view_up": [0.48981180389508683, 0.8647097694977263, -0.11118188386706776],
        "position": [-17.277630202755162, 13.419047188880267, 9.232808007244259],
        "view_angle": 30.0,
        "clipping_range": [11.403438348232822, 36.44815678922037],
    }

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["update_camera"]["rpc"],
        [
            {
                "camera_options": camera_options,
            }
        ],
    )
    assert server.compare_image(3, "viewer/update_camera.jpeg") == True


def test_render_now(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)

    camera_options = {
        "focal_point": [-0.034399999999999986, 2.4513515, -0.10266900000000012],
        "view_up": [0.48981180389508683, 0.8647097694977263, -0.11118188386706776],
        "position": [-17.277630202755162, 13.419047188880267, 9.232808007244259],
        "view_angle": 30.0,
        "clipping_range": [11.403438348232822, 36.44815678922037],
    }

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["update_camera"]["rpc"],
        [
            {
                "camera_options": camera_options,
            }
        ],
    )
    server.compare_image(1, "mesh/register.jpeg")

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["render_now"]["rpc"],
    )

    assert server.compare_image(3, "viewer/render_now.jpeg") == True


def test_set_z_scaling(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    dataset_factory(id="123456789", viewable_file_name="polygon_attribute.vtp")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image(3, "viewer/polygon_attribute.jpeg") == True

    dataset_factory(id="987654321", viewable_file_name="vertex_attribute.vtp")
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "987654321"}],
    )
    assert server.compare_image(3, "viewer/vertex_and_polygon_attribute.jpeg") == True

    camera_options = {
        "focal_point": [6.05, 5.7, 1.5],
        "view_up": [-0.019853719211915175, 0.9994261532466464, 0.02744438084681784],
        "position": [-19.898328271321652, 5.221831172558093, 0.1417477620371277],
        "view_angle": 30.0,
        "clipping_range": [20.16946812228507, 31.94497749971925],
    }

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["update_camera"]["rpc"],
        [
            {
                "camera_options": camera_options,
            }
        ],
    )
    server.compare_image(3, "mesh/register.jpeg")

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["set_z_scaling"]["rpc"],
        [{"z_scale": 2.5}],
    )
    assert server.compare_image(3, "viewer/set_z_scaling.jpeg") == True


def test_combined_scaling_and_grid(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["reset_visualization"]["rpc"],
    )
    assert server.compare_image(3, "viewer/reset_visualization.jpeg") == True
    dataset_factory(id="123456789", viewable_file_name="hat.vtp")
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image(3, "viewer/register_hat.jpeg") == True
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["grid_scale"]["rpc"],
        [{"visibility": True}],
    )
    assert server.compare_image(3, "viewer/grid_scale_on.jpeg") == True
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["set_z_scaling"]["rpc"],
        [{"z_scale": 2.5}],
    )
    assert server.compare_image(3, "viewer/combined_scaling_and_grid.jpeg") == True
