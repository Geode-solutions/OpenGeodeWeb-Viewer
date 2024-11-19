
# def test_set_model_mesh_visibility(server):

#     server.call("create_object_pipeline", [{"id": "123456789", "file_name": "CrossSection.vtm"}])
#     assert server.compare_image(3, "model.jpeg") == True
    
#     server.call("set_model_mesh_visibility", [{"id": "123456789", "visibility": True}])
#     assert server.compare_image(3, "set_model_mesh_visibility.jpeg") == True

# def test_set_model_components_visibility(server):

#     server.call("create_object_pipeline", [{"id": "123456789", "file_name": "CrossSection.vtm"}])
#     assert server.compare_image(3, "model.jpeg") == True

#     server.call("set_model_components_visibility", [{"id": "123456789", "visibility": False}])
#     assert server.compare_image(3, "set_model_components_visibility.jpeg") == True

def test_set_model_components_color(server):

    server.call("create_object_pipeline", [{"id": "123456789", "file_name": "CrossSection.vtm"}])
    assert server.compare_image(3, "model.jpeg") == True

    server.call("set_model_components_color", [{"id": "123456789", "red": 50, "green": 2, "blue": 250}])