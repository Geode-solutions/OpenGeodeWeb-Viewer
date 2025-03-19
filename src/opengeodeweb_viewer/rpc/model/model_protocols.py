# Standard library imports
import os

# Third party imports
import vtk
from vtkmodules.vtkRenderingCore import vtkCompositeDataDisplayAttributes
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.object.object_methods import VtkObjectView


class VtkModelView(VtkObjectView):
    model_prefix = "opengeodeweb_viewer.model."
    model_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self):
        super().__init__()

    @exportRpc(model_prefix + model_schemas_dict["register"]["rpc"])
    def registerModel(self, params):
        validate_schema(params, self.model_schemas_dict["register"], self.model_prefix)
        id, file_name = params["id"], params["file_name"]
        try:
            reader = vtk.vtkXMLMultiBlockDataReader()
            filter = vtk.vtkGeometryFilter()
            filter.SetInputConnection(reader.GetOutputPort())
            mapper = vtk.vtkCompositePolyDataMapper()
            mapper.SetInputConnection(filter.GetOutputPort())
            attributes = vtkCompositeDataDisplayAttributes()
            mapper.SetCompositeDataDisplayAttributes(attributes)
            self.registerObject(id, file_name, reader, filter, mapper)
        except Exception as e:
            print("error : ", str(e), flush=True)

    @exportRpc(model_prefix + model_schemas_dict["deregister"]["rpc"])
    def deregisterModel(self, params):
        validate_schema(
            params, self.model_schemas_dict["deregister"], self.model_prefix
        )
        id = params["id"]
        self.deregisterObject(id)

    @exportRpc(model_prefix + model_schemas_dict["points.visibility"]["rpc"])
    def setModelPointsVisibility(self, params):
        validate_schema(
            params, self.model_schemas_dict["points.visibility"], self.model_prefix
        )
        id, visibility = params["id"], params["visibility"]
        self.SetPointsVisibility(id, visibility)

    @exportRpc(model_prefix + model_schemas_dict["points.size"]["rpc"])
    def setModelPointsSize(self, params):
        validate_schema(
            params, self.model_schemas_dict["points.size"], self.model_prefix
        )
        id, size = params["id"], params["size"]
        self.SetPointsSize(id, size)

    @exportRpc(model_prefix + model_schemas_dict["edges.visibility"]["rpc"])
    def setModelEdgesVisibility(self, params):
        validate_schema(
            params, self.model_schemas_dict["edges.visibility"], self.model_prefix
        )
        id, visibility = params["id"], params["visibility"]
        self.SetEdgesVisibility(id, visibility)
