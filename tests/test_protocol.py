import os


def test_create_visualization(server):
    server.call("create_visualization")
    abs_path = os.path.abspath("./tests/data/images/create_visualization.jpeg")
    print(f"{abs_path=}", flush=True)
    assert server.compare_image(4, abs_path) == True


def test_reset_camera(server):
    server.call("reset_camera")
    abs_path = os.path.abspath("./tests/data/images/reset.jpeg")
    assert server.compare_image(4, abs_path) == True


def test_create_object_pipeline(server):
    data = os.path.abspath("./tests/data/hat.vtp")
    server.call("create_object_pipeline", [{"id": "123456", "file_name": data}])
    abs_path = os.path.abspath("./tests/data/images/create_object_pipeline.jpeg")
    assert server.compare_image(4, abs_path) == True


# def test_toggle_object_visibility(server):
#     data = os.path.abspath("./tests/data/hat.vtp")
#     server.call("create_object_pipeline", [{"id": "123456", "file_name": data}])
#     abs_path = os.path.abspath("./tests/data/images/create_object_pipeline.jpeg")
#     assert server.compare_image(4, abs_path) == True

#     server.call("toggle_object_visibility", [{"id": "123456", "is_visible": False}])
#     abs_path = os.path.abspath("./tests/data/images/toggle_object_visibility.jpeg")
#     assert server.compare_image(4, abs_path) == True
