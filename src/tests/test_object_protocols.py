
def test_register_object(server):
    server.call("object.register", [{"id": "123456", "file_name": "hat.vtp"}])
    assert server.compare_image(3, "viewer/create_object_pipeline.jpeg") == True


def test_delete_object_pipeline(server):
    server.call("create_object_pipeline", [{"id": "123456789", "file_name": "hat.vtp"}])
    assert server.compare_image(3, "viewer/create_object_pipeline.jpeg") == True

    server.call("delete_object_pipeline", [{"id": "123456789"}])
    assert server.compare_image(3, "viewer/delete_object_pipeline.jpeg") == True


def test_toggle_object_visibility(server):
    server.call("create_object_pipeline", [{"id": "123456789", "file_name": "hat.vtp"}])
    assert server.compare_image(3, "viewer/create_object_pipeline.jpeg") == True

    server.call("toggle_object_visibility", [{"id": "123456789", "visibility": False}])
    assert server.compare_image(3, "viewer/toggle_object_visibility_1.jpeg") == True

    server.call("toggle_object_visibility", [{"id": "123456789", "visibility": True}])
    assert server.compare_image(3, "viewer/toggle_object_visibility_2.jpeg") == True


def test_apply_textures(server):

    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    assert server.compare_image(3, "viewer/create_object_pipeline.jpeg") == True

    server.call(
        "apply_textures",
        [
            {
                "id": "123456789",
                "textures": [
                    {
                        "texture_name": "lambert2SG",
                        "texture_file_name": "hat_lambert2SG.vti",
                    }
                ],
            }
        ],
    )
    assert server.compare_image(3, "object/apply_textures.jpeg") == True

