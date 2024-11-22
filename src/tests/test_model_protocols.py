def test_register_model(server):

    server.call("model.register", [{"id": "123456789", "file_name": "CrossSection.vtm"}])
    assert server.compare_image(3, "model/register.jpeg") == True

# def test_deregister_model(server):

#     test_register_model(server)

#     server.call("model.deregister", [{"id": "123456789"}])
#     assert server.compare_image(3, "model/deregister.jpeg") == True


# def test_set_mesh_visibility(server):

#     test_register_model(server)
    
#     server.call("model.set_mesh_visibility", [{"id": "123456789", "visibility": True}])
#     assert server.compare_image(3, "model/set_mesh_visibility.jpeg") == True

# def test_set_components_visibility(server):

#     test_register_model(server)

#     server.call("model.set_components_visibility", [{"id": "123456789", "visibility": False}])
#     assert server.compare_image(3, "model/set_components_visibility.jpeg") == True

def test_set_components_color(server):

    test_register_model(server)

    server.call("model.set_components_color", [{"id": "123456789", "red": 255, "green": 192, "blue": 203}])
    assert server.compare_image(3, "model/set_components_color.jpeg") == True