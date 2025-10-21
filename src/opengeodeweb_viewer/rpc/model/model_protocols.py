# Standard library imports
import os

# Third party imports
import vtk
from vtkmodules.vtkRenderingCore import vtkCompositeDataDisplayAttributes
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.object.object_methods import VtkObjectView
from . import schemas


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
        params = schemas.Register.from_dict(params)
        data_id = params.id
        try:
            data = self.get_data(data_id)
            file_name = str(data["viewable_file_name"])

            reader = vtk.vtkXMLMultiBlockDataReader()
            filter = vtk.vtkGeometryFilter()
            filter.SetInputConnection(reader.GetOutputPort())
            mapper = vtk.vtkCompositePolyDataMapper()
            mapper.SetInputConnection(filter.GetOutputPort())
            attributes = vtkCompositeDataDisplayAttributes()
            mapper.SetCompositeDataDisplayAttributes(attributes)
            self.registerObject(data_id, file_name, reader, filter, mapper)
            self.get_object(data_id)["max_dimension"] = "default"
        except Exception as e:
            print(f"Error registering model {data_id}: {str(e)}", flush=True)
            raise

    @exportRpc(model_prefix + model_schemas_dict["deregister"]["rpc"])
    def deregisterModel(self, params):
        validate_schema(
            params, self.model_schemas_dict["deregister"], self.model_prefix
        )
        params = schemas.Deregister.from_dict(params)
        self.deregisterObject(params.id)

    @exportRpc(model_prefix + model_schemas_dict["visibility"]["rpc"])
    def setModelVisibility(self, params):
        validate_schema(
            params, self.model_schemas_dict["visibility"], self.model_prefix
        )
        params = schemas.Visibility.from_dict(params)
        self.SetVisibility(params.id, params.visibility)
