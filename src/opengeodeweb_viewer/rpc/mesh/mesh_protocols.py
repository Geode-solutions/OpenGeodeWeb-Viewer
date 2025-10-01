# Standard library imports
import os
from typing import Optional, Union, cast

# Third party imports
import vtk
from wslink import register as exportRpc
from opengeodeweb_microservice.database.data import Data

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.object.object_methods import VtkObjectView


class VtkMeshView(VtkObjectView):
    mesh_prefix = "opengeodeweb_viewer.mesh."
    mesh_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(mesh_prefix + mesh_schemas_dict["register"]["rpc"])
    def registerMesh(self, params: dict[str, Union[str, int, float, bool]]) -> None:
        validate_schema(params, self.mesh_schemas_dict["register"], self.mesh_prefix)
        data_id = str(params["id"])
        try:
            _ = self.get_data(data_id)
            file_path = self.get_data_file_path(data_id)

            reader = vtk.vtkXMLGenericDataObjectReader()
            reader.SetFileName(file_path)
            filter = {}
            mapper = vtk.vtkDataSetMapper()
            mapper.SetInputConnection(reader.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)

            renderer = self.get_renderer()
            renderer.AddActor(actor)

            self.register_object(data_id, reader, filter, actor, mapper, {})

            reader.Update()
            data_object = reader.GetOutput()
            data_set = vtk.vtkDataSet.SafeDownCast(data_object)
            cell_types = vtk.vtkCellTypes()
            data_set.GetCellTypes(cell_types)
            cell_data = cell_types.GetCellTypesArray()
            max_id = -1
            for t in range(cell_data.GetSize()):
                t_id = cell_data.GetValue(t)
                max_id = max(max_id, t_id)
            print(f"{max_id=}", flush=True)
            max_dimension = ""
            if max_id < 3:
                max_dimension = "points"
            elif max_id < 5:
                max_dimension = "edges"
            elif max_id < 7:
                max_dimension = "polygons"
            elif max_id >= 7:
                max_dimension = "polyhedra"
            self.get_data_base()[data_id]["max_dimension"] = max_dimension

            renderWindow = self.getView("-1")
            renderer.ResetCamera()
            renderWindow.Render()
            self.render()
        except Exception as e:
            print("error : ", str(e), flush=True)
            print(f"Error registering mesh {data_id}: {str(e)}", flush=True)
            raise

    @exportRpc(mesh_prefix + mesh_schemas_dict["deregister"]["rpc"])
    def deregisterMesh(self, params: dict[str, Union[str, int, float, bool]]) -> None:
        validate_schema(params, self.mesh_schemas_dict["deregister"], self.mesh_prefix)
        data_id = str(params["id"])
        self.deregisterObject(data_id)

    @exportRpc(mesh_prefix + mesh_schemas_dict["visibility"]["rpc"])
    def SetMeshVisibility(
        self, params: dict[str, Union[str, int, float, bool]]
    ) -> None:
        validate_schema(params, self.mesh_schemas_dict["visibility"], self.mesh_prefix)
        data_id, visibility = str(params["id"]), bool(params["visibility"])
        self.SetVisibility(data_id, visibility)

    @exportRpc(mesh_prefix + mesh_schemas_dict["opacity"]["rpc"])
    def setMeshOpacity(self, params: dict[str, Union[str, int, float, bool]]) -> None:
        validate_schema(params, self.mesh_schemas_dict["opacity"], self.mesh_prefix)
        data_id, opacity = str(params["id"]), params["opacity"]
        self.SetOpacity(data_id, opacity)

    @exportRpc(mesh_prefix + mesh_schemas_dict["color"]["rpc"])
    def setMeshColor(
        self,
        params: dict[
            str, Union[str, int, float, bool, dict[str, Union[str, int, float]]]
        ],
    ) -> None:
        validate_schema(params, self.mesh_schemas_dict["color"], self.mesh_prefix)
        color_dict = cast(dict[str, Union[str, int, float]], params["color"])
        data_id, red, green, blue = (
            str(params["id"]),
            int(color_dict["r"]),
            int(color_dict["g"]),
            int(color_dict["b"]),
        )
        self.SetColor(data_id, red, green, blue)

    @exportRpc(mesh_prefix + mesh_schemas_dict["apply_textures"]["rpc"])
    def meshApplyTextures(
        self, params: dict[str, Union[str, list[dict[str, str]]]]
    ) -> None:
        validate_schema(
            params, self.mesh_schemas_dict["apply_textures"], self.mesh_prefix
        )
        data_id = str(params["id"])
        textures_info = cast(list[dict[str, str]], params["textures"])
        self.applyTextures(data_id, textures_info)

    def applyTextures(self, mesh_id: str, textures_info: list[dict[str, str]]) -> None:
        for tex_info in textures_info:
            texture_id = tex_info["id"]
            texture_name = tex_info["texture_name"]
            texture_data = Data.get(texture_id)
            if not texture_data or texture_data.geode_object != "RasterImage2D":
                continue
            texture_file_path = self.get_data_file_path(texture_id)
            texture_reader = vtk.vtkXMLImageDataReader()
            texture_reader.SetFileName(texture_file_path)
            texture_reader.Update()
            texture = vtk.vtkTexture()
            texture.SetInputConnection(texture_reader.GetOutputPort())
            texture.InterpolateOn()
            reader = cast(vtk.vtkAlgorithm, self.get_object(mesh_id)["reader"])
            output = reader.GetOutput()
            point_data = output.GetPointData()
            for i in range(point_data.GetNumberOfArrays()):
                array = point_data.GetArray(i)
                if array.GetName() == texture_name:
                    point_data.SetTCoords(array)
                    break
            actor = cast(vtk.vtkActor, self.get_object(mesh_id)["actor"])
            actor.SetTexture(texture)
        self.render()

    def displayAttributeOnVertices(self, data_id: str, name: str) -> None:
        reader = self.get_object(data_id)["reader"]
        points = reader.GetOutput().GetPointData()
        points.SetActiveScalars(name)
        mapper = self.get_object(data_id)["mapper"]
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUsePointData()
        mapper.SetScalarRange(points.GetScalars().GetRange())
        self.render()

    def displayAttributeOnCells(self, data_id: str, name: str) -> None:
        reader = self.get_object(data_id)["reader"]
        cells = reader.GetOutput().GetCellData()
        cells.SetActiveScalars(name)
        mapper = self.get_object(data_id)["mapper"]
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUseCellData()
        mapper.SetScalarRange(cells.GetScalars().GetRange())
        self.render()
