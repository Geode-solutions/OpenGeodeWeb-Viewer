# Standard library imports
import os

# Third party imports
from wslink import register as exportRpc  # type: ignore
from vtkmodules.vtkIOXML import vtkXMLGenericDataObjectReader, vtkXMLImageDataReader
from vtkmodules.vtkRenderingCore import vtkDataSetMapper, vtkActor, vtkTexture
from vtkmodules.vtkCommonDataModel import vtkDataSet, vtkCellTypes
from vtkmodules.vtkCommonExecutionModel import vtkAlgorithm
from opengeodeweb_microservice.database.data import Data
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.utils_functions import (
    validate_schema,
    RpcParams,
)
from opengeodeweb_viewer.object.object_methods import VtkObjectView
from opengeodeweb_viewer.vtk_protocol import vtkData
from . import schemas


class VtkMeshView(VtkObjectView):
    mesh_prefix = "opengeodeweb_viewer.mesh."
    mesh_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(mesh_prefix + mesh_schemas_dict["register"]["rpc"])
    def registerMesh(self, rpc_params: RpcParams) -> None:
        print(f"{self.mesh_schemas_dict["register"]}", flush=True)
        validate_schema(
            rpc_params, self.mesh_schemas_dict["register"], self.mesh_prefix
        )
        params = schemas.Register.from_dict(rpc_params)
        data_id = params.id
        try:
            file_name = str(self.get_data(data_id)["viewable_file"])
            reader = vtkXMLGenericDataObjectReader()
            mapper = vtkDataSetMapper()
            mapper.SetInputConnection(reader.GetOutputPort())
            data = vtkData(reader, mapper)
            self.registerObject(data_id, file_name, data)
            data_object = reader.GetOutput()
            data_set = vtkDataSet.SafeDownCast(data_object)
            cell_types = vtkCellTypes()
            data_set.GetCellTypes(cell_types)
            cell_data = cell_types.GetCellTypesArray()
            max_id = -1
            for t in range(cell_data.GetSize()):
                t_id = cell_data.GetValue(t)
                max_id = max(max_id, t_id)
            print(f"{max_id=}", flush=True)
            if max_id < 3:
                data.max_dimension = "points"
            elif max_id < 5:
                data.max_dimension = "edges"
            elif max_id < 7:
                data.max_dimension = "polygons"
            elif max_id >= 7:
                data.max_dimension = "polyhedra"

        except Exception as e:
            print(f"Error registering mesh {data_id}: {str(e)}", flush=True)
            raise

    @exportRpc(mesh_prefix + mesh_schemas_dict["deregister"]["rpc"])
    def deregisterMesh(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.mesh_schemas_dict["deregister"], self.mesh_prefix
        )
        params = schemas.Deregister.from_dict(rpc_params)
        self.deregisterObject(params.id)

    @exportRpc(mesh_prefix + mesh_schemas_dict["visibility"]["rpc"])
    def SetMeshVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.mesh_schemas_dict["visibility"], self.mesh_prefix
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetVisibility(params.id, params.visibility)

    @exportRpc(mesh_prefix + mesh_schemas_dict["opacity"]["rpc"])
    def setMeshOpacity(self, rpc_params: RpcParams) -> None:
        validate_schema(rpc_params, self.mesh_schemas_dict["opacity"], self.mesh_prefix)
        params = schemas.Opacity.from_dict(rpc_params)
        self.SetOpacity(params.id, params.opacity)

    @exportRpc(mesh_prefix + mesh_schemas_dict["color"]["rpc"])
    def setMeshColor(self, rpc_params: RpcParams) -> None:
        validate_schema(rpc_params, self.mesh_schemas_dict["color"], self.mesh_prefix)
        params = schemas.Color.from_dict(rpc_params)
        color = params.color
        self.SetColor(params.id, color.r, color.g, color.b)

    @exportRpc(mesh_prefix + mesh_schemas_dict["apply_textures"]["rpc"])
    def meshApplyTextures(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.mesh_schemas_dict["apply_textures"], self.mesh_prefix
        )
        params = schemas.ApplyTextures.from_dict(rpc_params)
        mesh_id = params.id
        for tex_info in params.textures:
            texture_id = tex_info.id
            texture_data = Data.get(texture_id)
            if texture_data is None:
                continue
            texture_file = texture_data.viewable_file
            if texture_file is None or not texture_file.lower().endswith(".vti"):
                continue
            texture_file_path = self.get_data_file_path(texture_id)
            texture_reader = vtkXMLImageDataReader()
            texture_reader.SetFileName(texture_file_path)
            texture_reader.Update()
            texture = vtkTexture()
            texture.SetInputConnection(texture_reader.GetOutputPort())
            texture.InterpolateOn()
            reader = self.get_object(mesh_id).reader
            output = reader.GetOutputAsDataSet()
            point_data = output.GetPointData()
            for i in range(point_data.GetNumberOfArrays()):
                array = point_data.GetArray(i)
                if array.GetName() == tex_info.texture_name:
                    point_data.SetTCoords(array)
                    break
            actor = self.get_object(mesh_id).actor
            actor.SetTexture(texture)

    def displayAttributeOnVertices(self, data_id: str, name: str) -> None:
        reader = self.get_object(data_id).reader
        points = reader.GetOutputAsDataSet().GetPointData()
        points.SetActiveScalars(name)
        mapper = self.get_object(data_id).mapper
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUsePointData()
        mapper.SetScalarRange(points.GetScalars().GetRange())

    def displayAttributeOnCells(self, data_id: str, name: str) -> None:
        reader = self.get_object(data_id).reader
        cells = reader.GetOutputAsDataSet().GetCellData()
        cells.SetActiveScalars(name)
        mapper = self.get_object(data_id).mapper
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUseCellData()
        mapper.SetScalarRange(cells.GetScalars().GetRange())

    def displayScalarRange(self, data_id: str, minimum: float, maximum: float) -> None:
        mapper = self.get_object(data_id).mapper
        mapper.SetScalarRange(minimum, maximum)
