from collections.abc import Callable

from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from tests.conftest import ServerMonitor

# Local constants
mesh_id = "12345678901234567890123456789012"


def test_register_mesh(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    dataset_factory(data_id=mesh_id, viewable_file="hat.vtp", viewer_elements_type="polygons")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "name": "hat.vtp"}],
    )
    assert server.compare_image("mesh/register.jpeg")


def test_deregister_mesh(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["deregister"]["rpc"],
        [{"id": mesh_id}],
    )

    assert server.compare_image("mesh/deregister.jpeg")


def test_visibility(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": False}],
    )
    assert server.compare_image("mesh/visibility.jpeg")


def test_color(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["color"]["rpc"],
        [
            {
                "id": mesh_id,
                "color": {"red": 50, "green": 2, "blue": 250, "alpha": 1.0},
            }
        ],
    )
    assert server.compare_image("mesh/color.jpeg")


def test_apply_textures(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)
    dataset_factory(
        data_id="00000000000000000000000987654321",
        viewable_file="hat_lambert2SG.vti",
        viewer_elements_type="polygons",
    )

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["apply_textures"]["rpc"],
        [
            {
                "id": mesh_id,
                "textures": [
                    {
                        "texture_name": "lambert2SG",
                        "id": "00000000000000000000000987654321",
                    }
                ],
            }
        ],
    )
    assert server.compare_image("mesh/apply_textures.jpeg")
