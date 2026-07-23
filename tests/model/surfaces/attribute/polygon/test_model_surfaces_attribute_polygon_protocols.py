# Standard library imports
import glob
import os
from typing import Callable

# Third party imports
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader, vtkXMLPolyDataWriter
from vtkmodules.vtkCommonCore import vtkDoubleArray

from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from opengeodeweb_viewer.rpc.model.surfaces.model_surfaces_protocols import (
    VtkModelSurfacesView,
)
from opengeodeweb_viewer.rpc.model.surfaces.attribute.polygon.surfaces_attribute_polygon_protocols import (
    VtkModelSurfacesAttributePolygonView,
)

# Local application imports
from tests.conftest import ServerMonitor

model_id = "123456789"


def add_polygon_attribute_to_cube(model_id: str) -> None:
    data_folder = os.path.join(os.environ["DATA_FOLDER_PATH"], model_id)
    for filepath in glob.glob(
        os.path.join(data_folder, "**", "Surface_*.vtp"), recursive=True
    ):
        reader = vtkXMLPolyDataReader()
        reader.SetFileName(filepath)
        reader.Update()
        polydata = reader.GetOutput()

        num_cells = polydata.GetNumberOfCells()
        cell_array = vtkDoubleArray()
        cell_array.SetName("triangle_vertices")
        cell_array.SetNumberOfComponents(1)
        for i in range(num_cells):
            cell_array.InsertNextValue(float(i))

        polydata.GetCellData().AddArray(cell_array)

        writer = vtkXMLPolyDataWriter()
        writer.SetFileName(filepath)
        writer.SetInputData(polydata)
        writer.Write()


def register_model_cube_with_polygon_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:
    dataset_factory(id=model_id, viewable_file="cube.vtm")
    add_polygon_attribute_to_cube(model_id)
    server.call(
        VtkModelView.model_prefix + VtkModelView.model_schemas_dict["register"]["rpc"],
        [{"id": model_id, "name": "cube.vtm"}],
    )
    assert server.compare_image("model/cube_register.jpeg") == True


def test_surfaces_polygon_attribute(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    register_model_cube_with_polygon_attribute(server, dataset_factory)

    # Hide all blocks to ensure visibility of surfaces
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 50)), "visibility": False}],
    )
    # Show only surfaces
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(36, 47)), "visibility": True}],
    )

    server.call(
        VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_prefix
        + VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_schemas_dict[
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(36, 47)),
                "name": "triangle_vertices",
                "item": 0,
                "points": [
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                ],
                "minimum": 0.0,
                "maximum": 1.0,
            }
        ],
    )
    assert server.compare_image("model/surfaces/attribute.jpeg") == True


def test_surfaces_polygon_color_map(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    register_model_cube_with_polygon_attribute(server, dataset_factory)

    # Hide all blocks to ensure visibility of surfaces
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 50)), "visibility": False}],
    )
    # Show only surfaces
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(36, 47)), "visibility": True}],
    )

    # Set active polygon attribute, item, color map & range
    server.call(
        VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_prefix
        + VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_schemas_dict[
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(36, 47)),
                "name": "triangle_vertices",
                "item": 0,
                "points": [
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                ],
                "minimum": 0.0,
                "maximum": 1.0,
            }
        ],
    )

    assert server.compare_image("model/surfaces/color_map.jpeg") == True


def test_surfaces_polygon_color_map_range_update(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    register_model_cube_with_polygon_attribute(server, dataset_factory)

    # Hide all blocks to ensure visibility of surfaces
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 50)), "visibility": False}],
    )
    # Show only surfaces
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(36, 47)), "visibility": True}],
    )

    # Set active polygon attribute
    server.call(
        VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_prefix
        + VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_schemas_dict[
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(36, 47)),
                "name": "triangle_vertices",
                "item": 0,
                "points": [
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                ],
                "minimum": 0.0,
                "maximum": 1.0,
            }
        ],
    )

    assert server.compare_image("model/surfaces/color_map.jpeg") == True

    # Update range via attribute
    server.call(
        VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_prefix
        + VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_schemas_dict[
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(36, 47)),
                "name": "triangle_vertices",
                "item": 0,
                "points": [
                    40.0,
                    0.0,
                    0.0,
                    1.0,
                    45.0,
                    1.0,
                    0.0,
                    0.0,
                ],
                "minimum": 40.0,
                "maximum": 45.0,
            }
        ],
    )

    assert server.compare_image("model/surfaces/updated_color_map.jpeg") == True


def test_surfaces_polygon_color_map_red_shift(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    register_model_cube_with_polygon_attribute(server, dataset_factory)

    # Hide all blocks to ensure visibility of surfaces
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 50)), "visibility": False}],
    )
    # Show only surfaces
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(36, 47)), "visibility": True}],
    )

    # Set active polygon attribute
    server.call(
        VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_prefix
        + VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_schemas_dict[
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(36, 47)),
                "name": "triangle_vertices",
                "item": 0,
                "points": [
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                ],
                "minimum": 0.0,
                "maximum": 1.0,
            }
        ],
    )

    assert server.compare_image("model/surfaces/color_map.jpeg") == True

    # Update range via attribute
    server.call(
        VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_prefix
        + VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_schemas_dict[
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(36, 47)),
                "name": "triangle_vertices",
                "item": 0,
                "points": [
                    3.0,
                    0.0,
                    0.0,
                    1.0,
                    4.0,
                    1.0,
                    0.0,
                    0.0,
                ],
                "minimum": 3.0,
                "maximum": 4.0,
            }
        ],
    )

    assert server.compare_image("model/surfaces/color_map_red_shift.jpeg") == True


def test_surfaces_polygon_color_map_rainbow(
    server: ServerMonitor, dataset_factory: Callable[..., str]
) -> None:

    register_model_cube_with_polygon_attribute(server, dataset_factory)

    # Hide all blocks to ensure visibility of surfaces
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(1, 50)), "visibility": False}],
    )
    # Show only surfaces
    server.call(
        VtkModelSurfacesView.model_surfaces_prefix
        + VtkModelSurfacesView.model_surfaces_schemas_dict["visibility"]["rpc"],
        [{"id": model_id, "block_ids": list(range(36, 47)), "visibility": True}],
    )

    # Rainbow Desaturated Map
    server.call(
        VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_prefix
        + VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_schemas_dict[
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(36, 47)),
                "name": "triangle_vertices",
                "item": 0,
                "points": [
                    0.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    0.143 * 50,
                    0,
                    0,
                    92 / 255,
                    0.285 * 50,
                    0,
                    255 / 255,
                    255 / 255,
                    0.429 * 50,
                    0,
                    128 / 255,
                    0,
                    0.571 * 50,
                    255 / 255,
                    255 / 255,
                    0,
                    0.714 * 50,
                    255 / 255,
                    97 / 255,
                    0,
                    0.857 * 50,
                    107 / 255,
                    0,
                    0,
                    50.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 0.0,
                "maximum": 50.0,
            }
        ],
    )

    assert server.compare_image("model/surfaces/color_map_rainbow_initial.jpeg") == True

    # Update rainbow range via attribute
    server.call(
        VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_prefix
        + VtkModelSurfacesAttributePolygonView.model_surfaces_attribute_polygon_schemas_dict[
            "attribute"
        ][
            "rpc"
        ],
        [
            {
                "id": model_id,
                "block_ids": list(range(36, 47)),
                "name": "triangle_vertices",
                "item": 0,
                "points": [
                    5.0,
                    71 / 255,
                    71 / 255,
                    219 / 255,
                    5.0 + 0.143 * 10,
                    0,
                    0,
                    92 / 255,
                    5.0 + 0.285 * 10,
                    0,
                    255 / 255,
                    255 / 255,
                    5.0 + 0.429 * 10,
                    0,
                    128 / 255,
                    0,
                    5.0 + 0.571 * 10,
                    255 / 255,
                    255 / 255,
                    0,
                    5.0 + 0.714 * 10,
                    255 / 255,
                    97 / 255,
                    0,
                    5.0 + 0.857 * 10,
                    107 / 255,
                    0,
                    0,
                    15.0,
                    224 / 255,
                    77 / 255,
                    77 / 255,
                ],
                "minimum": 5.0,
                "maximum": 15.0,
            }
        ],
    )

    assert server.compare_image("model/surfaces/color_map_rainbow.jpeg") == True
