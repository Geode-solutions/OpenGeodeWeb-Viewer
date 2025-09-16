from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView
from ..test_data_helpers import create_mesh_data


def test_register_mesh(server):
    mesh_id = create_mesh_data("hat.vtp")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "file_name": "hat.vtp"}],
    )
    assert server.compare_image(3, "mesh/register.jpeg") == True
    return mesh_id


def test_deregister_mesh(server):
    mesh_id = create_mesh_data("hat.vtp")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "file_name": "hat.vtp"}],
    )
    server.compare_image(3, "mesh/register.jpeg")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["deregister"]["rpc"],
        [{"id": mesh_id}],
    )
    assert server.compare_image(3, "mesh/deregister.jpeg") == True


def test_opacity(server):
    mesh_id = create_mesh_data("hat.vtp")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "file_name": "hat.vtp"}],
    )
    server.compare_image(3, "mesh/register.jpeg")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["opacity"]["rpc"],
        [{"id": mesh_id, "opacity": 0.1}],
    )
    assert server.compare_image(3, "mesh/opacity.jpeg") == True


def test_visibility(server):
    mesh_id = create_mesh_data("hat.vtp")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "file_name": "hat.vtp"}],
    )
    server.compare_image(3, "mesh/register.jpeg")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["visibility"]["rpc"],
        [{"id": mesh_id, "visibility": False}],
    )
    assert server.compare_image(3, "mesh/visibility.jpeg") == True


def test_color(server):
    mesh_id = create_mesh_data("hat.vtp")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "file_name": "hat.vtp"}],
    )
    server.compare_image(3, "mesh/register.jpeg")

    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["color"]["rpc"],
        [{"id": mesh_id, "color": {"r": 50, "g": 2, "b": 250}}],
    )
    assert server.compare_image(3, "mesh/color.jpeg") == True


def test_apply_textures(server):
    mesh_id = create_mesh_data("hat.vtp")
    server.call(
        VtkMeshView.mesh_prefix + VtkMeshView.mesh_schemas_dict["register"]["rpc"],
        [{"id": mesh_id, "file_name": "hat.vtp"}],
    )
    server.compare_image(3, "mesh/register.jpeg")

    server.call(
        VtkMeshView.mesh_prefix
        + VtkMeshView.mesh_schemas_dict["apply_textures"]["rpc"],
        [
            {
                "id": mesh_id,
                "textures": [
                    {
                        "texture_name": "lambert2SG",
                        "texture_file_name": "hat_lambert2SG.vti",
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
