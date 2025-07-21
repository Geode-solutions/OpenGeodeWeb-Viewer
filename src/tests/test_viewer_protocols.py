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


def test_update_camera(server):
    test_register_mesh(server)

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


def test_render_now(server):
    test_register_mesh(server)

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


def test_set_z_scaling(server):

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "12345678", "file_name": "polygon_attribute.vtp"}],
    )
    assert server.compare_image(3, "viewer/polygon_attribute.jpeg") == True

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "123456789", "file_name": "vertex_attribute.vtp"}],
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


def test_combined_scaling_and_grid(server):
    # test_set_z_scaling(server)

    # server.call(
    #     VtkViewerView.viewer_prefix
    #     + VtkViewerView.viewer_schemas_dict["set_background_color"]["rpc"],
    #     [{"color": {"r": 180, "g": 180, "b": 180}}],
    # )
    # assert server.compare_image(3, "viewer/scaling_and_grid_color.jpeg") == True

    # server.call(
    #     VtkViewerView.viewer_prefix
    #     + VtkViewerView.viewer_schemas_dict["grid_scale"]["rpc"],
    #     [{"visibility": True}],
    # )

    # assert server.compare_image(3, "viewer/grid_scale_on.jpeg") == True
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

    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["set_z_scaling"]["rpc"],
        [{"z_scale": 2.5}],
    )

    assert server.compare_image(3, "viewer/combined_scaling_and_grid.jpeg") == True
