import os


def test_create_visualization(server):
    server.call("viewer.create_visualization")
    assert server.compare_image(3, "viewer/create_visualization.jpeg") == True


def test_reset_camera(server):
    server.call("viewer.reset_camera")
    assert server.compare_image(3, "viewer/reset_camera.jpeg") == True

def test_set_viewer_background_color(server):
    server.call("viewer.set_background_color", [{"red": 0, "green": 0, "blue": 255}])
    assert server.compare_image(3, "viewer/set_background_color.jpeg") == True

def test_get_point_position(server):

    server.call(
        "mesh.register",
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    assert server.compare_image(3, "mesh/register.jpeg") == True

    server.call("viewer.get_point_position", [{"x": 0, "y": 0}])
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


def test_take_screenshot(server):
    # Create an object
    server.call(
        "mesh.register",
        [{"id": "123456789", "file_name": "hat.vtp"}],
    )
    assert server.compare_image(3, "mesh/register.jpeg") == True


    # Take a screenshot with background jpg
    server.call(
        "viewer.take_screenshot",
        [{"filename": "take_screenshot_with_background", "output_extension": "jpg", "include_background": True}],
    )

    response = server.get_response()
    blob = server.get_response()
    assert type(blob) is bytes

    with open(os.path.join(server.test_output_dir, "test.jpg"), "wb") as f:
        f.write(blob)
        f.close()
    first_image_path = os.path.join(server.test_output_dir, "test.jpg")
    second_image_path = os.path.join(server.images_dir_path, "viewer/take_screenshot_with_background.jpg")

    assert server.images_diff(first_image_path, second_image_path) == 0.0

    # Take a screenshot without background png
    server.call(
        "viewer.take_screenshot",
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
    second_image_path = os.path.join(server.images_dir_path, "viewer/take_screenshot_without_background.png")

    assert server.images_diff(first_image_path, second_image_path) == 0.0

    # Take a screenshot with background png
    server.call(
        "viewer.take_screenshot",
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
    second_image_path = os.path.join(server.images_dir_path, "viewer/take_screenshot_with_background.png")

    assert server.images_diff(first_image_path, second_image_path) == 0.0
