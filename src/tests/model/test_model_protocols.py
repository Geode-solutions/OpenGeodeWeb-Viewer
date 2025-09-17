from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView

def test_register_model(server, dataset_factory):

    dataset_factory(id="123456789", viewable_file_name="CrossSection.vtm")
    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image(3, "model/register.jpeg") == True


def test_register_model_cube(server, dataset_factory):

    dataset_factory(id="123456789", viewable_file_name="cube.vtm")
    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image(3, "model/cube_register.jpeg") == True


def test_visibility_model(server, dataset_factory):

    test_register_model(server, dataset_factory)

    server.call(
        VtkModelView.model_prefix
        + VtkModelView.model_schemas_dict["visibility"]["rpc"],
        [{"id": "123456789", "visibility": False}],
    )
    assert server.compare_image(3, "model/visibility.jpeg") == True


def test_deregister_model(server, dataset_factory):

    test_register_model(server, dataset_factory)

    server.call(
        VtkModelView.model_prefix
        + VtkModelView.model_schemas_dict["deregister"]["rpc"],
        [{"id": "123456789"}],
    )
    assert server.compare_image(3, "model/deregister.jpeg") == True
