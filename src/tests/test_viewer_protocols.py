# Standard library imports
import os

# Third party imports
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView


# Local application imports
from .mesh.test_mesh_protocols import test_register_mesh


def test_reset_visualization(server):
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["reset_visualization"]["rpc"]
    )
    assert server.compare_image(3, "viewer/reset_visualization.jpeg") == True


def test_reset_camera(server):
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["reset_camera"]["rpc"]
    )
    assert server.compare_image(3, "viewer/reset_camera.jpeg") == True


def test_set_viewer_background_color(server):
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["set_background_color"]["rpc"],
        [{"color": {"r": 0, "g": 0, "b": 255}}],
    )
    assert server.compare_image(3, "viewer/set_background_color.jpeg") == True


def test_get_point_position(server):
    test_register_mesh(server)

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["get_point_position"]["rpc"],
        [{"x": 0, "y": 0}],
    )
    response = server.get_response()
    assert "x" in response["result"]
    assert "y" in response["result"]
    assert "z" in response["result"]
    x = response["result"]["x"]
    y = response["result"]["y"]
    z = response["result"]["z"]
    assert type(x) is float
    assert type(y) is float
    assert type(z) is float


def test_take_screenshot(server):
    # Create an object
    test_register_mesh(server)

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

    response = server.get_response()
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

    response = server.get_response()
    response = server.get_response()
    blob = server.get_response()
    print(f"{blob=}", flush=True)
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

    response = server.get_response()
    response = server.get_response()
    blob = server.get_response()
    print(f"{blob=}", flush=True)
    assert type(blob) is bytes

    with open(os.path.join(server.test_output_dir, "test.png"), "wb") as f:
        f.write(blob)
        f.close()
    first_image_path = os.path.join(server.test_output_dir, "test.png")
    second_image_path = os.path.join(
        server.images_dir_path, "viewer/take_screenshot_with_background.png"
    )

    assert server.images_diff(first_image_path, second_image_path) == 0.0


def test_picked_ids(server):

    test_register_mesh(server)

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["picked_ids"]["rpc"],
        [{"x": 100, "y": 200, "ids": ["123456789"]}],
    )
    response = server.get_response()

    print(f"Response: {response}", flush=True)

    assert "result" in response, f"Key 'result' not found in response: {response}"

    assert (
        "array_ids" in response["result"]
    ), f"Key 'array_ids' not found in response['result']: {response['result']}"

    array_ids = response["result"]["array_ids"]
    assert isinstance(array_ids, list), f"Expected a list, but got {type(array_ids)}"
    assert all(isinstance(id, str) for id in array_ids), "All IDs should be strings"
    assert len(array_ids) > 0, "The list of array_ids should not be empty"


def test_grid_scale(server):

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["reset_visualization"]["rpc"],
    )

    assert server.compare_image(3, "viewer/reset_visualization.jpeg") == True

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    assert server.compare_image(3, "viewer/register_hat.jpeg") == True

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["grid_scale"]["rpc"],
        [{"visibility": True}],
    )

    assert server.compare_image(3, "viewer/grid_scale_on.jpeg") == True


def test_axes(server):

    test_reset_visualization(server)

    server.call(
        VtkViewerView.viewer_prefix + VtkViewerView.viewer_schemas_dict["axes"]["rpc"],
        [{"visibility": False}],
    )

    assert server.compare_image(3, "viewer/axes_off.jpeg") == True
