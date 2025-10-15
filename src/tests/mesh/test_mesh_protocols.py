from typing import Callable
from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from tests.conftest import ServerMonitor


def test_register_mesh(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    dataset_factory(id="123456789", viewable_file_name="hat.vtp")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image(3, "mesh/register.jpeg") == True


def test_deregister_mesh(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["deregister"]["rpc"],
        [{"id": "123456789"}],
    )

    assert server.compare_image(3, "mesh/deregister.jpeg") == True


def test_opacity(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["opacity"]["rpc"],
        [{"id": "123456789", "opacity": 0.1}],
    )
    assert server.compare_image(3, "mesh/opacity.jpeg") == True


def test_visibility(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image(3, "mesh/visibility.jpeg") == True


def test_color(server: ServerMonitor, dataset_factory: Callable[..., str]) -> None:
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["color"]["rpc"],
        [{"id": "123456789", "color": {"r": 50, "g": 2, "b": 250}}],
    )
    assert server.compare_image(3, "mesh/color.jpeg") == True


def test_apply_textures(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    test_register_mesh(server, dataset_factory)
    texture_entry = dataset_factory(
        id="987654321", viewable_file_name="hat_lambert2SG.vti"
    )

    server.call(
        VtkMeshView.mesh_prefix
        + VtkMeshView.mesh_schemas_dict["apply_textures"]["rpc"],
        [
            {
                "id": "123456789",
                "textures": [
                    {
                        "texture_name": "lambert2SG",
                        "id": "987654321",
                    }
                ],
            }
        ],
    )
    assert server.compare_image(3, "mesh/apply_textures.jpeg") == True


# def test_display_vertex_attribute(server):
#     server.call(VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"], [{"id": "123456789", "file_name": "vertex_attribute.vtp"}])
#     assert server.compare_image(3, "mesh/display_vertex_attribute_1.jpeg") == True

#     server.call(
#         VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["display_vertex_attribute"]["rpc"],
#         [{"id": "123456789", "name": "geode_implicit_attribute"}],
#     )
#     assert server.compare_image(3, "mesh/display_vertex_attribute_2.jpeg") == True


#     server.call(
#         VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["color"]["rpc"],
#         [{"id": "123456789", "red": 250, "green": 0, "blue": 0}],
#     )
#     assert server.compare_image(3, "mesh/display_vertex_attribute_3.jpeg") == True

# def test_display_polygon_attribute(server):
#     server.call(VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"], [{"id": "123456789", "file_name": "polygon_attribute.vtp"}])
#     assert server.compare_image(3, "mesh/display_polygon_attribute_1.jpeg") == True

#     server.call(
#         VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["display_polygon_attribute"]["rpc"],
#         [{"id": "123456789", "name": "implicit_on_polygons"}],
#     )
#     assert server.compare_image(3, "mesh/display_polygon_attribute_2.jpeg") == True
