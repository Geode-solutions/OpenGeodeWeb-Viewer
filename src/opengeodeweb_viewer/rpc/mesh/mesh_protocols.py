# Standard library imports
import os

# Third party imports
import vtk
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.object.object_methods import VtkObjectView


class VtkMeshView(VtkObjectView):
    mesh_prefix = "opengeodeweb_viewer.mesh."
    mesh_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self):
        super().__init__()

    @exportRpc(mesh_prefix + mesh_schemas_dict["register"]["rpc"])
    def registerMesh(self, params):
        validate_schema(params, self.mesh_schemas_dict["register"], self.mesh_prefix)
        id, file_name = params["id"], params["file_name"]
        try:
            reader = vtk.vtkXMLGenericDataObjectReader()
            filter = {}
            mapper = vtk.vtkDataSetMapper()
            mapper.SetInputConnection(reader.GetOutputPort())
            self.registerObject(id, file_name, reader, filter, mapper)

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
            self.get_data_base()[id]["max_dimension"] = max_dimension
        except Exception as e:
            print("error : ", str(e), flush=True)

    @exportRpc(mesh_prefix + mesh_schemas_dict["deregister"]["rpc"])
    def deregisterMesh(self, params):
        validate_schema(params, self.mesh_schemas_dict["deregister"], self.mesh_prefix)
        id = params["id"]
        self.deregisterObject(id)

    @exportRpc(mesh_prefix + mesh_schemas_dict["visibility"]["rpc"])
    def SetMeshVisibility(self, params):
        validate_schema(params, self.mesh_schemas_dict["visibility"], self.mesh_prefix)
        id, visibility = params["id"], params["visibility"]
        self.SetVisibility(id, visibility)

    @exportRpc(mesh_prefix + mesh_schemas_dict["opacity"]["rpc"])
    def setMeshOpacity(self, params):
        validate_schema(params, self.mesh_schemas_dict["opacity"], self.mesh_prefix)
        id, opacity = params["id"], params["opacity"]
        self.SetOpacity(id, opacity)

    @exportRpc(mesh_prefix + mesh_schemas_dict["color"]["rpc"])
    def setMeshColor(self, params):
        validate_schema(params, self.mesh_schemas_dict["color"], self.mesh_prefix)
        id, red, green, blue = (
            params["id"],
            params["color"]["r"],
            params["color"]["g"],
            params["color"]["b"],
        )
        self.SetColor(id, red, green, blue)

    @exportRpc(mesh_prefix + mesh_schemas_dict["apply_textures"]["rpc"])
    def meshApplyTextures(self, params):
        validate_schema(
            params, self.mesh_schemas_dict["apply_textures"], self.mesh_prefix
        )
        id, textures = params["id"], params["textures"]
        self.applyTextures(id, textures)

    def displayAttributeOnVertices(self, id, name):
        reader = self.get_object(id)["reader"]
        points = reader.GetOutput().GetPointData()
        points.SetActiveScalars(name)
        mapper = self.get_object(id)["mapper"]
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUsePointData()
        mapper.SetScalarRange(points.GetScalars().GetRange())
        self.render()

    def displayAttributeOnCells(self, id, name):
        reader = self.get_object(id)["reader"]
        cells = reader.GetOutput().GetCellData()
        cells.SetActiveScalars(name)
        mapper = self.get_object(id)["mapper"]
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUseCellData()
        mapper.SetScalarRange(cells.GetScalars().GetRange())
        self.render()
