from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView

def test_register_model(server):

    server.call(VtkModelView.prefix + VtkModelView.schemas_dict["register"]["rpc"], [{"id": "123456789", "file_name": "CrossSection.vtm"}])
    assert server.compare_image(3, "model/register.jpeg") == True

def test_deregister_model(server):

    test_register_model(server)

    server.call(VtkModelView.prefix + VtkModelView.schemas_dict["deregister"]["rpc"], [{"id": "123456789"}])
    assert server.compare_image(3, "model/deregister.jpeg") == True


def test_set_mesh_visibility(server):

    test_register_model(server)
    
    server.call(VtkModelView.prefix + VtkModelView.schemas_dict["set_mesh_visibility"]["rpc"], [{"id": "123456789", "visibility": True}])
    assert server.compare_image(3, "model/set_mesh_visibility.jpeg") == True

def test_set_components_visibility(server):

    test_register_model(server)

    server.call(VtkModelView.prefix + VtkModelView.schemas_dict["set_components_visibility"]["rpc"], [{"id": "123456789", "visibility": False}])
    assert server.compare_image(3, "model/set_components_visibility.jpeg") == True

def test_set_components_color(server):

    test_register_model(server)

    server.call(VtkModelView.prefix + VtkModelView.schemas_dict["set_components_color"]["rpc"], [{"id": "123456789", "red": 255, "green": 0, "blue": 0}])
    assert server.compare_image(3, "model/set_components_color.jpeg") == True