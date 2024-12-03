

from opengeodeweb_viewer.rpc.mesh.mesh_protocols import VtkMeshView

def test_register_mesh(server):

    server.call(VtkMeshView.prefix + VtkMeshView.schemas_dict["register"]["rpc"], [{"id": "123456789", "file_name": "hat.vtp"}])
    assert server.compare_image(3, "mesh/register.jpeg") == True

def test_deregister_mesh(server):

    test_register_mesh(server)

    server.call(VtkMeshView.prefix + VtkMeshView.schemas_dict["deregister"]["rpc"], [{"id": "123456789"}])
    assert server.compare_image(3, "mesh/deregister.jpeg") == True

def test_set_opacity(server):

    test_register_mesh(server)

    server.call(VtkMeshView.prefix + VtkMeshView.schemas_dict["set_opacity"]["rpc"], [{"id": "123456789", "opacity": 0.1}])
    assert server.compare_image(3, "mesh/set_opacity.jpeg") == True

def test_set_edge_visibility(server):

    test_register_mesh(server)

    server.call(VtkMeshView.prefix + VtkMeshView.schemas_dict["set_edge_visibility"]["rpc"], [{"id": "123456789", "visibility": True}])
    assert server.compare_image(3, "mesh/set_edge_visibility.jpeg") == True

# def test_set_point_visibility(server):

#     test_register_mesh(server)

#     server.call(VtkMeshView.prefix + VtkMeshView.schemas_dict["set_point_visibility"]["rpc"], [{"id": "123456789", "visibility": True}])
#     assert server.compare_image(3, "mesh/set_point_visibility.jpeg") == True

# def test_set_point_size(server):

#     server.call(VtkMeshView.prefix + VtkMeshView.schemas_dict["register"]["rpc"], [{"id": "123456789", "file_name": "vertex_attribute.vtp"}])
#     assert server.compare_image(3, "mesh/set_point_size_1.jpeg") == True

    # server.call(VtkMeshView.prefix + VtkMeshView.schemas_dict["set_point_visibility"]["rpc"], [{"id": "123456789", "visibility": True}])
    # assert server.compare_image(3, "mesh/set_point_size_2.jpeg") == True

    # server.call(VtkMeshView.prefix + VtkMeshView.schemas_dict["set_point_size"]["rpc"], [{"id": "123456789", "size": 10}])
    # assert server.compare_image(3, "mesh/set_point_size_3.jpeg") == True


def test_set_color(server):

    test_register_mesh(server)

    server.call(VtkMeshView.prefix + VtkMeshView.schemas_dict["set_color"]["rpc"], [{"id": "123456789", "red": 50, "green": 2, "blue": 250}])
    assert server.compare_image(3, "mesh/set_color.jpeg") == True


def test_display_vertex_attribute(server):
    server.call(VtkMeshView.prefix + VtkMeshView.schemas_dict["register"]["rpc"], [{"id": "123456789", "file_name": "vertex_attribute.vtp"}])
    assert server.compare_image(3, "mesh/display_vertex_attribute_1.jpeg") == True

    server.call(
        VtkMeshView.prefix + VtkMeshView.schemas_dict["display_vertex_attribute"]["rpc"],
        [{"id": "123456789", "name": "geode_implicit_attribute"}],
    )
    assert server.compare_image(3, "mesh/display_vertex_attribute_2.jpeg") == True


    server.call(
        VtkMeshView.prefix + VtkMeshView.schemas_dict["set_color"]["rpc"],
        [{"id": "123456789", "red": 250, "green": 0, "blue": 0}],
    )
    assert server.compare_image(3, "mesh/display_vertex_attribute_3.jpeg") == True

def test_display_polygon_attribute(server):
    server.call(VtkMeshView.prefix + VtkMeshView.schemas_dict["register"]["rpc"], [{"id": "123456789", "file_name": "polygon_attribute.vtp"}])
    assert server.compare_image(3, "mesh/display_polygon_attribute_1.jpeg") == True

    server.call(
        VtkMeshView.prefix + VtkMeshView.schemas_dict["display_polygon_attribute"]["rpc"],
        [{"id": "123456789", "name": "implicit_on_polygons"}],
    )
    assert server.compare_image(3, "mesh/display_polygon_attribute_2.jpeg") == True