

def test_set_opacity(server):

    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    assert server.compare_image(3, "create_object_pipeline.jpeg") == True

    server.call("set_opacity", [{"id": "123456789", "opacity": 0.1}])
    assert server.compare_image(3, "set_opacity.jpeg") == True


def test_toggle_edge_visibility(server):

    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    assert server.compare_image(3, "create_object_pipeline.jpeg") == True

    server.call("toggle_edge_visibility", [{"id": "123456789", "visibility": True}])
    assert server.compare_image(3, "toggle_edge_visibility.jpeg") == True


def test_toggle_edge_visibility(server):

    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    assert server.compare_image(3, "create_object_pipeline.jpeg") == True

    server.call("toggle_edge_visibility", [{"id": "123456789", "visibility": False}])
    assert server.compare_image(3, "toggle_edge_visibility.jpeg") == True

def test_toggle_point_visibility(server):

    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "verts.vtp"}],
    )

    assert server.compare_image(3, "toggle_point_visibility.jpeg") == True
    server.call("toggle_point_visibility", [{"id": "123456789", "visibility": True}])
    assert server.compare_image(3, "toggle_point_visibility.jpeg") == True

def test_set_point_size(server):

    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "verts.vtp"}],
    )
    assert server.compare_image(3, "set_point_size_1.jpeg") == True

    server.call("toggle_point_visibility", [{"id": "123456789", "visibility": True}])
    assert server.compare_image(3, "set_point_size_1.jpeg") == True

    server.call("set_point_size", [{"id": "123456789", "size": 10}])
    assert server.compare_image(2, "set_point_size.jpeg") == True


def test_set_color(server):

    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    assert server.compare_image(3, "create_object_pipeline.jpeg") == True

    server.call("set_color", [{"id": "123456789", "red": 50, "green": 2, "blue": 250}])
    assert server.compare_image(3, "set_color.jpeg") == True


def test_display_vertex_attribute(server):
    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "vertex_attribute.vtp"}],
    )
    assert server.compare_image(3, "display_vertex_attribute_1.jpeg") == True
    server.call(
        "display_vertex_attribute",
        [{"id": "123456789", "name": "geode_implicit_attribute"}],
    )
    assert server.compare_image(3, "display_vertex_attribute_2.jpeg") == True