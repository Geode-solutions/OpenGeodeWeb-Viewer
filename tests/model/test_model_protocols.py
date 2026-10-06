from typing import Callable
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.rpc.model.blocks.model_blocks_protocols import (
    VtkModelBlocksView,
)
from opengeodeweb_viewer.rpc.viewer.viewer_protocols import VtkViewerView
from tests.conftest import ServerMonitor

# Local constants
model_id = "12345678901234567890123456789012"


def test_register_model(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    dataset_factory(id=model_id, viewable_file="CrossSection.vtm")
    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": model_id, "name": "cube.vtm"}],
    )
    assert server.compare_image("model/register.jpeg") == True


def test_register_model_cube(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    dataset_factory(id=model_id, viewable_file="cube.vtm")
    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": model_id, "name": "cube.vtm"}],
    )
    assert server.compare_image("model/cube_register.jpeg") == True


def test_register_model_implicit_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    dataset_factory(id=model_id, viewable_file="implicit_attribute.vtm")
    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": model_id, "name": "implicit_attribute.vtm"}],
    )
    assert server.compare_image("model/implicit_attribute_register.jpeg") == True


def test_visibility_model(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model(server, dataset_factory)

    server.call(
        VtkModelView.model_prefix
        + VtkModelView.model_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "visibility": False}],
    )
    assert server.compare_image("model/visibility.jpeg") == True


def test_deregister_model(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model(server, dataset_factory)

    server.call(
        VtkModelView.model_prefix
        + VtkModelView.model_schemas_dict["deregister"]["rpc"],
        [{"id": model_id}],
    )
    assert server.compare_image("model/deregister.jpeg") == True


def test_get_blocks_bounds(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model(server, dataset_factory)

    rpc = VtkModelView.model_prefix + "get_blocks_bounds"
    server.call(rpc, [{"id": "12345678901234567890123456789012", "block_ids": [2]}])

    response = server.get_response()
    while isinstance(response, bytes) or response.get("id") != f"rpc:{rpc}":
        response = server.get_response()

    assert response.get("result") == {"bounds": [4.9, 4.9, 3.1, 3.1, 0.0, 0.0]}


def test_model_cube_side_view(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_model_cube(server, dataset_factory)
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["update_camera"]["rpc"],
        [
            {
                "camera_options": {
                    "focal_point": [5.0, 5.0, 7.5],
                    "view_up": [0.0, 0.0, 1.0],
                    "position": [40.0, -30.0, 20.0],
                    "view_angle": 30.0,
                    "clipping_range": [1.0, 100.0],
                }
            }
        ],
    )
    assert server.compare_image("model/cube_side_view.jpeg") == True


def test_model_explode(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_model_cube_side_view(server, dataset_factory)
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["explode"]["rpc"],
        [{"ids": [model_id], "explode_factor": 1.0}],
    )
    assert server.compare_image("model/explode.jpeg") == True


def test_model_explode_removed(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_model_explode(server, dataset_factory)
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["explode"]["rpc"],
        [{"ids": [model_id], "explode_factor": 0.0}],
    )
    assert server.compare_image("model/cube_side_view.jpeg") == True


def test_model_explode_blocks_color(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_model_explode(server, dataset_factory)
    server.call(
        VtkModelBlocksView.model_blocks_prefix
        + VtkModelBlocksView.model_blocks_schemas_dict["color"]["rpc"],
        [
            {
                "id": model_id,
                "block_ids": [48],
                "color_mode": "constant",
                "color": {"red": 255, "green": 0, "blue": 0, "alpha": 1.0},
            }
        ],
    )
    assert server.compare_image("model/explode_blocks_color.jpeg") == True


def test_model_explode_then_shrink(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_model_explode(server, dataset_factory)
    server.call(
        VtkViewerView.viewer_prefix
        + VtkViewerView.viewer_schemas_dict["shrink"]["rpc"],
        [{"ids": [model_id], "shrink_factor": 0.8}],
    )
    assert server.compare_image("model/explode_then_shrink.jpeg") == True


def test_model_explode_blocks_visibility(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_model_explode(server, dataset_factory)
    server.call(
        VtkModelBlocksView.model_blocks_prefix
        + VtkModelBlocksView.model_blocks_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": [49], "visibility": False}],
    )
    assert server.compare_image("model/explode_blocks_visibility.jpeg") == True


def test_model_explode_all_hidden(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_model_explode(server, dataset_factory)
    server.call(
        VtkModelBlocksView.model_blocks_prefix
        + VtkModelBlocksView.model_blocks_schemas_dict["visibility"]["rpc"],
        [
            {
                "id": model_id,
                "block_ids": list(range(1, 50)),
                "visibility": False,
            }
        ],
    )
    assert server.compare_image("model/explode_all_hidden.jpeg") == True
