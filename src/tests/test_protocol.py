import os


def test_create_visualization(server):
    server.call("create_visualization")
    assert server.compare_image(3, "create_visualization.jpeg") == True


def test_reset_camera(server):
    server.call("reset_camera")
    assert server.compare_image(3, "reset_camera.jpeg") == True


def test_create_object_pipeline(server):
    server.call("create_object_pipeline", [{"id": "123456", "file_name": "hat.vtp"}])
    assert server.compare_image(3, "create_object_pipeline.jpeg") == True


def test_delete_object_pipeline(server):
    server.call("create_object_pipeline", [{"id": "123456789", "file_name": "hat.vtp"}])
    assert server.compare_image(3, "create_object_pipeline.jpeg") == True

    server.call("delete_object_pipeline", [{"id": "123456789"}])
    assert server.compare_image(3, "delete_object_pipeline.jpeg") == True


def test_toggle_object_visibility(server):
    server.call("create_object_pipeline", [{"id": "123456789", "file_name": "hat.vtp"}])
    assert server.compare_image(3, "create_object_pipeline.jpeg") == True

    server.call("toggle_object_visibility", [{"id": "123456789", "is_visible": False}])
    assert server.compare_image(3, "toggle_object_visibility_1.jpeg") == True

    server.call("toggle_object_visibility", [{"id": "123456789", "is_visible": True}])
    assert server.compare_image(3, "toggle_object_visibility_2.jpeg") == True


def test_apply_textures(server):

    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    assert server.compare_image(3, "create_object_pipeline.jpeg") == True

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
    assert server.compare_image(3, "apply_textures.jpeg") == True


def test_get_point_position(server):

    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    assert server.compare_image(3, "create_object_pipeline.jpeg") == True

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
    assert server.compare_image(3, "create_object_pipeline.jpeg") == True

    server.call("toggle_edge_visibility", [{"id": "123456789", "visibility": True}])
    assert server.compare_image(3, "toggle_edge_visibility.jpeg") == True


def test_set_color(server):

    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    assert server.compare_image(3, "create_object_pipeline.jpeg") == True

    server.call("set_color", [{"id": "123456789", "red": 50, "green": 2, "blue": 250}])
    assert server.compare_image(3, "set_color.jpeg") == True



def test_take_screenshot(server):
    # Create an object
    server.call(
        "create_object_pipeline",
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    assert server.compare_image(3, "create_object_pipeline.jpeg") == True


    # Take a screenshot with background jpg
    server.call(
        "take_screenshot",
        [{"filename": "take_screenshot_with_background", "output_extension": "jpg", "include_background": True}],
    )

    response = server.get_response()
    blob = server.get_response()
    assert type(blob) is bytes

    with open(os.path.join(server.test_output_dir, "test.jpg"), "wb") as f:
        f.write(blob)
        f.close()
    first_image_path = os.path.join(server.test_output_dir, "test.jpg")
    second_image_path = os.path.join(server.images_dir_path, "take_screenshot_with_background.jpg")

    assert server.images_diff(first_image_path, second_image_path) == 0.0

    # Take a screenshot without background png
    server.call(
        "take_screenshot",
        [{"filename": "take_screenshot_without_background", "output_extension": "png", "include_background": True}],
    )
    
    response = server.get_response()
    response = server.get_response()
    blob = server.get_response()
    print(f"{blob=}", flush=True)
    assert type(blob) is bytes

    with open(os.path.join(server.test_output_dir, "test.png"), "wb") as f:
        f.write(blob)
        f.close()
    first_image_path = os.path.join(server.test_output_dir, "test.png")
    second_image_path = os.path.join(server.images_dir_path, "take_screenshot_without_background.png")

    assert server.images_diff(first_image_path, second_image_path) == 0.0

    # Take a screenshot with background png
    server.call(
        "take_screenshot",
        [{"filename": "take_screenshot_with_background", "output_extension": "png", "include_background": True}],
    )
    
    response = server.get_response()
    response = server.get_response()
    blob = server.get_response()
    print(f"{blob=}", flush=True)
    assert type(blob) is bytes

    with open(os.path.join(server.test_output_dir, "test.png"), "wb") as f:
        f.write(blob)
        f.close()
    first_image_path = os.path.join(server.test_output_dir, "test.png")
    second_image_path = os.path.join(server.images_dir_path, "take_screenshot_with_background.png")

    assert server.images_diff(first_image_path, second_image_path) == 0.0
