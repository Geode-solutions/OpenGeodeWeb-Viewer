from opengeodeweb_viewer.rpc.generic.generic_protocols import VtkGenericView


def test_register_mesh(server, dataset_factory):
    data_id = "123456789"
    dataset_factory(id=data_id, viewable_file_name="hat.vtp", geode_object="mesh")

    server.call(
        VtkGenericView.generic_prefix
        + VtkGenericView.generic_schemas_dict["register"]["rpc"],
        [{"viewer_object": "mesh", "id": data_id}],
    )
    assert server.compare_image(3, "mesh/register.jpeg") is True


def test_register_model(server, dataset_factory):
    data_id = "123456789"
    dataset_factory(id=data_id, viewable_file_name="CrossSection.vtm")

    server.call(
        VtkGenericView.generic_prefix
        + VtkGenericView.generic_schemas_dict["register"]["rpc"],
        [{"viewer_object": "model", "id": data_id}],
    )
    assert server.compare_image(3, "model/register.jpeg") is True


def test_deregister_mesh(server, dataset_factory):
    test_register_mesh(server, dataset_factory)

    server.call(
        VtkGenericView.generic_prefix
        + VtkGenericView.generic_schemas_dict["deregister"]["rpc"],
        [{"viewer_object": "mesh", "id": "123456789"}],
    )
    assert server.compare_image(3, "mesh/deregister.jpeg") == True


def test_deregister_model(server, dataset_factory):
    test_register_model(server, dataset_factory)

    server.call(
        VtkGenericView.generic_prefix
        + VtkGenericView.generic_schemas_dict["deregister"]["rpc"],
        [{"viewer_object": "model", "id": "123456789"}],
    )
    assert server.compare_image(3, "model/deregister.jpeg") == True
