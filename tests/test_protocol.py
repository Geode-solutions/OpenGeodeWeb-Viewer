from vtk_protocol import VtkView


def test_create_visualization():
    VtkView.create_visualization(VtkView)
    assert True
