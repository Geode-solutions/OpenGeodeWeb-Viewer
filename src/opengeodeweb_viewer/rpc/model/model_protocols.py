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
        print(
            self.model_prefix + self.model_schemas_dict["register"]["rpc"],
            f"{params=}",
            flush=True,
        )
        validate_schema(params, self.model_schemas_dict["register"])
        id = params["id"]
        file_name = params["file_name"]
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
        print(
            self.model_prefix + self.model_schemas_dict["deregister"]["rpc"],
            f"{params=}",
            flush=True,
        )
        validate_schema(params, self.model_schemas_dict["deregister"])
        id = params["id"]
        self.deregisterObject(id)

    @exportRpc(model_prefix + model_schemas_dict["points.visibility"]["rpc"])
    def setModelPointsVisibility(self, params):
        print(
            self.model_prefix + self.model_schemas_dict["points.visibility"]["rpc"],
            f"{params=}",
            flush=True,
        )
        validate_schema(params, self.model_schemas_dict["points.visibility"])
        id, visibility = params["id"], params["visibility"]
        self.SetPointsVisibility(id, visibility)

    @exportRpc(model_prefix + model_schemas_dict["points.size"]["rpc"])
    def setModelPointsSize(self, params):
        print(
            self.model_prefix + self.model_schemas_dict["points.size"]["rpc"],
            f"{params=}",
            flush=True,
        )
        validate_schema(params, self.model_schemas_dict["points.size"])
        id, size = params["id"], params["size"]
        self.SetPointsSize(id, size)

    @exportRpc(model_prefix + model_schemas_dict["edges.visibility"]["rpc"])
    def setModelEdgesVisibility(self, params):
        print(
            self.model_prefix + self.model_schemas_dict["edges.visibility"]["rpc"],
            f"{params=}",
            flush=True,
        )
        validate_schema(params, self.model_schemas_dict["edges.visibility"])
        id, visibility = params["id"], params["visibility"]
        self.SetEdgesVisibility(id, visibility)
