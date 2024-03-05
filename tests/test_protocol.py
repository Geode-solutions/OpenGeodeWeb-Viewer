import os

images_dir_path = os.path.abspath("./tests/data/images")


# def test_create_visualization(server):
#     server.call("create_visualization", [])
#     abs_path = os.path.join(images_dir_path, "create_visualization.jpeg")
#     assert server.compare_image(3, abs_path) == True


# def test_reset_camera(server):
#     server.call("reset_camera", [])
#     abs_path = os.path.join(images_dir_path, "reset_camera.jpeg")
#     assert server.compare_image(3, abs_path) == True


def test_create_object_pipeline(server):
    server.call("create_object_pipeline", [{"id": "123456", "file_name": "hat.vtp"}])
    abs_path = os.path.join(images_dir_path, "create_object_pipeline.jpeg")
    assert server.compare_image(3, abs_path) == True


def test_delete_object_pipeline(server):
    server.call("create_object_pipeline", [{"id": "123456789", "file_name": "hat.vtp"}])
    abs_path = os.path.join(images_dir_path, "create_object_pipeline.jpeg")
    assert server.compare_image(3, abs_path) == True

    server.call("delete_object_pipeline", [{"id": "123456789"}])
    abs_path = os.path.join(images_dir_path, "delete_object_pipeline.jpeg")
    assert server.compare_image(3, abs_path) == True


def test_toggle_object_visibility(server):
    server.call("create_object_pipeline", [{"id": "123456789", "file_name": "hat.vtp"}])
    abs_path = os.path.join(images_dir_path, "create_object_pipeline.jpeg")
    assert server.compare_image(3, abs_path) == True

    server.call("toggle_object_visibility", [{"id": "123456789", "is_visible": False}])
    abs_path = os.path.join(images_dir_path, "toggle_object_visibility_1.jpeg")
    assert server.compare_image(3, abs_path) == True

    server.call("toggle_object_visibility", [{"id": "123456789", "is_visible": True}])
    abs_path = os.path.join(images_dir_path, "toggle_object_visibility_2.jpeg")
    assert server.compare_image(3, abs_path) == True


def test_apply_textures(server):

    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "emperor_penguin.vtp"}],
    )
    abs_path = os.path.join(images_dir_path, "apply_textures_1.jpeg")
    assert server.compare_image(3, abs_path) == True

    server.call(
        "apply_textures",
        [
            {
                "id": "123456789",
                "textures": [
                    {
                        "texture_name": "PenguinMat",
                        "texture_file_name": "penguin_colors.vti",
                    }
                ],
            }
        ],
    )
    abs_path = os.path.join(images_dir_path, "apply_textures_2.jpeg")
    assert server.compare_image(3, abs_path) == True


def test_get_point_position(server):

    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    abs_path = os.path.join(images_dir_path, "get_point_position.jpeg")
    assert server.compare_image(3, abs_path) == True

    server.call("get_point_position", [{"x": 0, "y": 0}])
    response = server.get_response()
    assert "x" in response["result"]
    assert "y" in response["result"]
    assert "z" in response["result"]
    x = response["result"]["x"]
    y = response["result"]["y"]
    z = response["result"]["z"]
    assert type(x) is float
    assert type(y) is float
    assert type(z) is float
