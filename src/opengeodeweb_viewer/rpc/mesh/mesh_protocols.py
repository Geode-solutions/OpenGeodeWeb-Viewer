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
    mesh_schemas_dict = get_schemas_dict(os.path.join(os.path.dirname(__file__), "schemas"))

    def __init__(self):
        super().__init__()

    @exportRpc(mesh_prefix + mesh_schemas_dict["register"]["rpc"])
    def registerMesh(self, params):
        print(self.mesh_prefix + self.mesh_schemas_dict["register"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.mesh_schemas_dict["register"])
        id = params["id"]
        file_name = params["file_name"]
        try:
            reader = vtk.vtkXMLGenericDataObjectReader()
            filter = {}
            mapper = vtk.vtkDataSetMapper()
            mapper.SetInputConnection(reader.GetOutputPort())
            self.registerObject(id, file_name, reader, filter, mapper)
        except Exception as e:
            print("error : ", str(e), flush=True)

    @exportRpc(mesh_prefix + mesh_schemas_dict["deregister"]["rpc"])
    def deregisterMesh(self, params):
        print(self.mesh_prefix + self.mesh_schemas_dict["deregister"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.mesh_schemas_dict["deregister"])
        id = params["id"]
        self.deregisterObject(id)

    @exportRpc(mesh_prefix + mesh_schemas_dict["visibility"]["rpc"])
    def SetMeshVisibility(self, params):
        print(self.mesh_prefix + self.mesh_schemas_dict["visibility"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.mesh_schemas_dict["visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        self.SetVisibility(id, visibility)

    @exportRpc(mesh_prefix + mesh_schemas_dict["opacity"]["rpc"])
    def setMeshOpacity(self, params):
        print(self.mesh_prefix + self.mesh_schemas_dict["opacity"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.mesh_schemas_dict["opacity"])
        id = params["id"]
        opacity = float(params["opacity"])
        self.SetOpacity(id, opacity)

    @exportRpc(mesh_prefix + mesh_schemas_dict["color"]["rpc"])
    def setMeshColor(self, params):
        print(self.mesh_prefix + self.mesh_schemas_dict["color"]["rpc"], f"{params=}", flush=True)
        validate_schema(params, self.mesh_schemas_dict["color"])
        id = params["id"]
        red, green, blue = params["color"]["r"], params["color"]["g"], params["color"]["b"]
        self.SetColor(id, red, green, blue)

    def setMeshVertexAttribute(self, id, name):
        reader = self.get_object(id)["reader"]
        points = reader.GetOutput().GetPointData()
        points.SetActiveScalars(name)
        mapper = self.get_object(id)["mapper"]
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUsePointData()
        mapper.SetScalarRange(points.GetScalars().GetRange())
        self.render()

    def setMeshPolygonAttribute(self, id, name):
        reader = self.get_object(id)["reader"]
        cells = reader.GetOutput().GetCellData()
        cells.SetActiveScalars(name)
        mapper = self.get_object(id)["mapper"]
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUseCellData()
        mapper.SetScalarRange(cells.GetScalars().GetRange())
        self.render()