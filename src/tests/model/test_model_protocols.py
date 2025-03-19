from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView


def test_register_model(server):

    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": "123456789", "file_name": "CrossSection.vtm"}],
    )
    assert server.compare_image(3, "model/register.jpeg") == True


def test_register_model_cube(server):

    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": "123456789", "file_name": "cube.vtm"}],
    )
    assert server.compare_image(3, "model/cube_register.jpeg") == True


def test_deregister_model(server):

    test_register_model(server)

    server.call(
        VtkModelView.model_prefix
        + VtkModelView.model_schemas_dict["deregister"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image(3, "model/deregister.jpeg") == True


def test_edges_visibility(server):

    test_register_model(server)

    server.call(
        VtkModelView.model_prefix
        + VtkModelView.model_schemas_dict["edges.visibility"]["rpc"],
        [{"id": "123456789", "visibility": True}],
    )
    assert server.compare_image(3, "model/edges.visibility.jpeg") == True


def test_points_visibility(server):

    test_register_model(server)

    server.call(
        VtkModelView.model_prefix
        + VtkModelView.model_schemas_dict["points.visibility"]["rpc"],
        [{"id": "123456789", "visibility": True}],
    )
    assert server.compare_image(3, "model/points.visibility.jpeg") == True


def test_points_size(server):

    test_points_visibility(server)

    server.call(
        VtkModelView.model_prefix
        + VtkModelView.model_schemas_dict["points.size"]["rpc"],
        [{"id": "123456789", "size": 20}],
    )
    assert server.compare_image(3, "model/points.size.jpeg") == True
