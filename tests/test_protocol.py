import os

images_dir_path = os.path.abspath("./tests/data/images")


def test_create_visualization(server):
    server.call("create_visualization")
    abs_path = os.path.join(images_dir_path, "create_visualization.jpeg")
    assert server.compare_image(3, abs_path) == True


def test_reset_camera(server):
    server.call("reset_camera")
    abs_path = os.path.join(images_dir_path, "reset_camera.jpeg")
    assert server.compare_image(3, abs_path) == True


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
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    abs_path = os.path.join(images_dir_path, "create_object_pipeline.jpeg")
    assert server.compare_image(3, abs_path) == True

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
    abs_path = os.path.join(images_dir_path, "apply_textures.jpeg")
    assert server.compare_image(3, abs_path) == True


def test_get_point_position(server):

    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    abs_path = os.path.join(images_dir_path, "create_object_pipeline.jpeg")
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


def test_toggle_edge_visibility(server):

    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    abs_path = os.path.join(images_dir_path, "create_object_pipeline.jpeg")
    assert server.compare_image(3, abs_path) == True

    server.call("toggle_edge_visibility", [{"id": "123456789", "visibility": True}])
    abs_path = os.path.join(images_dir_path, "toggle_edge_visibility.jpeg")
    assert server.compare_image(3, abs_path) == True


def test_set_color(server):

    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    abs_path = os.path.join(images_dir_path, "create_object_pipeline.jpeg")
    assert server.compare_image(3, abs_path) == True

    server.call("set_color", [{"id": "123456789", "red": 50, "green": 2, "blue": 250}])
    abs_path = os.path.join(images_dir_path, "set_color.jpeg")
    assert server.compare_image(3, abs_path) == True
