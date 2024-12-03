from opengeodeweb_viewer.rpc.generic.generic_protocols import VtkGenericView

def test_register_mesh(server):
    server.call(VtkGenericView.prefix + VtkGenericView.schemas_dict["register"]["rpc"], [{"viewer_object": "mesh", "id": "123456789", "file_name": "hat.vtp"}])
    assert server.compare_image(3, "mesh/register.jpeg") == True

def test_register_model(server):
    server.call(VtkGenericView.prefix + VtkGenericView.schemas_dict["register"]["rpc"], [{"viewer_object": "model", "id": "123456789", "file_name": "CrossSection.vtm"}])
    assert server.compare_image(3, "model/register.jpeg") == True

def test_deregister_mesh(server):
    test_register_mesh(server)

    server.call(VtkGenericView.prefix + VtkGenericView.schemas_dict["deregister"]["rpc"], [{"viewer_object": "mesh", "id": "123456789"}])
    assert server.compare_image(3, "mesh/deregister.jpeg") == True

def test_deregister_model(server):
    test_register_model(server)

    server.call(VtkGenericView.prefix + VtkGenericView.schemas_dict["deregister"]["rpc"], [{"viewer_object": "model", "id": "123456789"}])
    assert server.compare_image(3, "model/deregister.jpeg") == True