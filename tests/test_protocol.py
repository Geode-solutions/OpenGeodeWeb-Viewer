def test_create_visualization(server):
    server.call("create_visualization")
    server.compare_image(9, "./data/images/create_visualization.jpg")

    assert True
