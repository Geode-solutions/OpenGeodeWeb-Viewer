# Standard library imports
import os

# Third party imports
from vtkmodules.vtkRenderingCore import (
    vtkCompositeDataDisplayAttributes,
    vtkCompositePolyDataMapper,
)
from vtkmodules.vtkIOXML import vtkXMLMultiBlockDataReader
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from wslink import register as exportRpc  # type: ignore
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.utils_functions import (
    validate_schema,
    RpcParams,
)
from opengeodeweb_viewer.object.object_methods import VtkObjectView
from opengeodeweb_viewer.vtk_protocol import VtkPipeline
from . import schemas


class VtkModelView(VtkObjectView):
    model_prefix = "opengeodeweb_viewer.model."
    model_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(model_prefix + model_schemas_dict["register"]["rpc"])
    @exportRpc(model_prefix + model_schemas_dict["register"]["rpc"])
    def registerModel(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.model_schemas_dict["register"], self.model_prefix
        )
        params = schemas.Register.from_dict(rpc_params)
        data_id = params.id
        try:
            file_name = str(self.get_viewer_data(data_id).viewable_file)
            reader = vtkXMLMultiBlockDataReader()
            reader.SetFileName(os.path.join(self.DATA_FOLDER_PATH, data_id, file_name))
            reader.Update()
            filter = vtkGeometryFilter()
            filter.SetInputConnection(reader.GetOutputPort())
            filter.Update()
            geometry_output = filter.GetOutputDataObject(0)
            mapper = vtkCompositePolyDataMapper()
            mapper.SetInputDataObject(geometry_output)
            attributes = vtkCompositeDataDisplayAttributes()
            mapper.SetCompositeDataDisplayAttributes(attributes)
            data = VtkPipeline(reader, mapper, filter)
            iterator = geometry_output.NewTreeIterator()
            iterator.InitTraversal()
            while not iterator.IsDoneWithTraversal():
                block = iterator.GetCurrentDataObject()
                if block:
                    flat_index = iterator.GetCurrentFlatIndex()
                    while flat_index > len(data.blockDataSets):
                        data.blockDataSets.append(None)
                    data.blockDataSets.append(block)
                iterator.GoToNextItem()

            multiblock_output = reader.GetOutput()
            category_iterator = multiblock_output.NewIterator()
            category_iterator.InitTraversal()
            while not category_iterator.IsDoneWithTraversal():
                category_block = category_iterator.GetCurrentDataObject()
                category_name = multiblock_output.GetMetaData(
                    category_iterator.GetCurrentIndex()
                ).Get(category_block.NAME())
                if category_block is not None:
                    category_filter = vtkGeometryFilter()
                    category_filter.SetInputDataObject(category_block)
                    category_filter.Update()
                    category_mapper = vtkCompositePolyDataMapper()
                    category_mapper.SetInputDataObject(
                        category_filter.GetOutputDataObject(0)
                    )
                    category_actor = vtkActor()
                    category_actor.SetMapper(category_mapper)
                    data.category_actors[category_name] = category_actor
                category_iterator.GoToNextItem()
            self.registerObject(data_id, file_name, data)
        except Exception as e:
            print(f"Error registering model {data_id}: {str(e)}", flush=True)
            raise

    @exportRpc(model_prefix + model_schemas_dict["deregister"]["rpc"])
    def deregisterModel(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.model_schemas_dict["deregister"], self.model_prefix
        )
        params = schemas.Deregister.from_dict(rpc_params)
        self.deregisterObject(params.id)

    @exportRpc(model_prefix + model_schemas_dict["visibility"]["rpc"])
    def setModelVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.model_schemas_dict["visibility"], self.model_prefix
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetVisibility(params.id, params.visibility)

    @exportRpc(model_prefix + model_schemas_dict["components_color"]["rpc"])
    def setModelComponentsColor(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.model_schemas_dict["components_color"], self.model_prefix
        )
        params = schemas.ComponentsColor.from_dict(rpc_params)
        color = params.color
        self.SetBlocksColor(params.id, params.block_ids, color.r, color.g, color.b)
