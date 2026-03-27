from typing import Callable
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from tests.conftest import ServerMonitor


def test_register_model(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    dataset_factory(id="123456789", viewable_file="CrossSection.vtm")
    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image("model/register.jpeg") == True


def test_register_model_cube(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    dataset_factory(id="123456789", viewable_file="cube.vtm")
    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image("model/cube_register.jpeg") == True


def test_visibility_model(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model(server, dataset_factory)

    server.call(
        VtkModelView.model_prefix
        + VtkModelView.model_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image("model/visibility.jpeg") == True


def test_deregister_model(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model(server, dataset_factory)

    server.call(
        VtkModelView.model_prefix
        + VtkModelView.model_schemas_dict["deregister"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image("model/deregister.jpeg") == True


def test_components_color_model(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    test_register_model_cube(server, dataset_factory)

    server.call(
        VtkModelView.model_prefix
        + VtkModelView.model_schemas_dict["components_color"]["rpc"],
        [
            {
                "id": "123456789",
                "block_ids": [48, 49],
                "color": {"r": 255, "g": 0, "b": 0},
            }
        ],
    )
    assert server.compare_image("model/components_color.jpeg") == True


def test_components_visibility_color_model(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_model_cube(server, dataset_factory)

    server.call(
        VtkModelView.model_prefix + "components_visibility",
        [{"id": "123456789", "block_ids": [48, 49], "visibility": False}],
    )

    server.call(
        VtkModelView.model_prefix + "components_color",
        [
            {
                "id": "123456789",
                "block_ids": list(range(36, 47)),
                "color": {"r": 0, "g": 255, "b": 0},
            }
        ],
    )
    assert server.compare_image("model/components_visibility_color.jpeg") == True
