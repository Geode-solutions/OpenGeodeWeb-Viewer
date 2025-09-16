from opengeodeweb_viewer.rpc.generic.generic_protocols import VtkGenericView
from .test_data_helpers import create_mesh_data, create_model_data


def test_register_mesh(server):
    mesh_id = create_mesh_data("hat.vtp")
    server.call(
        VtkGenericView.generic_prefix
        + VtkGenericView.generic_schemas_dict["register"]["rpc"],
        [{"viewer_object": "mesh", "id": mesh_id, "file_name": "hat.vtp"}],
    )
    assert server.compare_image(3, "mesh/register.jpeg") == True
    return mesh_id


def test_register_model(server):
    model_id = create_model_data("CrossSection.vtm")
    server.call(
        VtkGenericView.generic_prefix
        + VtkGenericView.generic_schemas_dict["register"]["rpc"],
        [
            {
                "viewer_object": "model",
                "id": model_id,
                "file_name": "CrossSection.vtm",
            }
        ],
    )
    assert server.compare_image(3, "model/register.jpeg") == True
    return model_id


def test_deregister_mesh(server):
    mesh_id = create_mesh_data("hat.vtp")
    server.call(
        VtkGenericView.generic_prefix
        + VtkGenericView.generic_schemas_dict["register"]["rpc"],
        [{"viewer_object": "mesh", "id": mesh_id, "file_name": "hat.vtp"}],
    )
    server.compare_image(3, "mesh/register.jpeg")
    server.call(
        VtkGenericView.generic_prefix
        + VtkGenericView.generic_schemas_dict["deregister"]["rpc"],
        [{"viewer_object": "mesh", "id": mesh_id}],
    )
    assert server.compare_image(3, "mesh/deregister.jpeg") == True


def test_deregister_model(server):
    model_id = create_model_data("CrossSection.vtm")
    server.call(
        VtkGenericView.generic_prefix
        + VtkGenericView.generic_schemas_dict["register"]["rpc"],
        [
            {
                "viewer_object": "model",
                "id": model_id,
                "file_name": "CrossSection.vtm",
            }
        ],
    )
    server.compare_image(3, "model/register.jpeg")
    server.call(
        VtkGenericView.generic_prefix
        + VtkGenericView.generic_schemas_dict["deregister"]["rpc"],
        [{"viewer_object": "model", "id": model_id}],
    )
    assert server.compare_image(3, "model/deregister.jpeg") == True
